/**
 * @file wideband_uart_flash.cpp
 * @brief Programs the on-board wideband MCU (STM32F042, FOME/rusEFI "f0_module") through its ROM serial bootloader.
 *
 * Wiring (daughterboard rev 0.4):
 *   PD8  USART3_TX  ->  F042 PA10 (USART1_RX)
 *   PD9  USART3_RX  <-  F042 PA9  (USART1_TX)
 *   PD10 push-pull  ->  F042 BOOT0 (10k pull-down on the board)
 *   PD11 open drain ->  F042 NRST
 *
 * The main MCU raises BOOT0, resets the F042 into ST's system-memory bootloader and speaks the USART bootloader
 * protocol (ST application note AN3155, 8 data bits, even parity): sync, mass erase, write the image at 0x08000000,
 * read it back to verify, then drops BOOT0 and resets the F042 into its new firmware.
 *
 * The image is rusEFI's own release/rc/wideband_image_with_bl.bin (CAN bootloader + wideband firmware), taken from
 * the wideband submodule of the rusEFI tree being built (see WBO_IMAGE in board.mk). Once that bootloader is on the
 * chip, rusEFI's normal "Update wideband firmware" over CAN works too.
 */

#include "pch.h"
#include "wideband_uart_flash.h"

#if !defined(EFI_BOOTLOADER) && EFI_PROD_CODE

#ifndef WBO_IMAGE_PATH
#error "WBO_IMAGE_PATH must point at wideband_image_with_bl.bin (set in board.mk)"
#endif

#if !STM32_SERIAL_USE_USART3
#error "USART3 must be enabled for the wideband programming link (STM32_SERIAL_USE_USART3 in board.mk)"
#endif

// The wideband image, pulled straight into flash at build time.
__asm__(
	".section .rodata.wbo_image,\"a\",%progbits\n"
	".balign 4\n"
	".global wbo_image_start\n"
	"wbo_image_start:\n"
	".incbin \"" WBO_IMAGE_PATH "\"\n"
	".global wbo_image_end\n"
	"wbo_image_end:\n"
	".previous\n");
extern "C" const uint8_t wbo_image_start[];
extern "C" const uint8_t wbo_image_end[];

namespace {

constexpr uint32_t F042_FLASH_BASE = 0x08000000;
constexpr size_t F042_FLASH_SIZE = 32 * 1024;
constexpr uint16_t F042_PRODUCT_ID = 0x445; // STM32F04x

constexpr uint8_t ACK = 0x79;
constexpr uint8_t NACK = 0x1F;

constexpr uint8_t BL_CMD_GET = 0x00;
constexpr uint8_t BL_CMD_GET_ID = 0x02;
constexpr uint8_t BL_CMD_READ = 0x11;
constexpr uint8_t BL_CMD_WRITE = 0x31;
constexpr uint8_t BL_CMD_ERASE = 0x43;
constexpr uint8_t BL_CMD_EXT_ERASE = 0x44;

constexpr size_t WRITE_CHUNK = 256; // protocol maximum, must be a multiple of 4
constexpr size_t VERIFY_CHUNK = 64; // ACK + 64 bytes fits the 128-byte serial queue set in board.mk

constexpr sysinterval_t BYTE_TIMEOUT = TIME_MS2I(200);
constexpr sysinterval_t WRITE_TIMEOUT = TIME_MS2I(1000);
constexpr sysinterval_t ERASE_TIMEOUT = TIME_MS2I(10000);

const SerialConfig wboSerialConfig = {
	.speed = 115200,
	// 9-bit frame = 8 data bits + parity; PCE alone (PS = 0) selects even parity
	.cr1 = USART_CR1_M | USART_CR1_PCE,
	.cr2 = 0,
	.cr3 = 0,
};

THD_WORKING_AREA(wboFlashStack, 1024);
volatile bool wboBusy = false;
const char* volatile wboStatus = "not run since power-up";

// --- pins -------------------------------------------------------------------------------------------------------

void setBoot0(bool high) {
	palWritePad(GPIOD, 10, high ? PAL_HIGH : PAL_LOW);
}

void pulseReset(uint32_t afterMs) {
	palClearPad(GPIOD, 11);
	chThdSleepMilliseconds(10);
	palSetPad(GPIOD, 11); // open drain: released, the F042's internal pull-up takes NRST high
	chThdSleepMilliseconds(afterMs);
}

void linkUp() {
	palSetPadMode(GPIOD, 8, PAL_MODE_ALTERNATE(7));
	palSetPadMode(GPIOD, 9, PAL_MODE_ALTERNATE(7) | PAL_STM32_PUPDR_PULLUP);
	sdStart(&SD3, &wboSerialConfig);
}

void linkDown() {
	sdStop(&SD3);
	palSetPadMode(GPIOD, 8, PAL_MODE_INPUT_PULLUP);
	palSetPadMode(GPIOD, 9, PAL_MODE_INPUT_PULLUP);
}

// --- AN3155 primitives ------------------------------------------------------------------------------------------

int getByte(sysinterval_t timeout) {
	msg_t m = sdGetTimeout(&SD3, timeout);
	return m < 0 ? -1 : (m & 0xFF);
}

void put(const uint8_t* data, size_t size) {
	sdWrite(&SD3, data, size);
}

void flushRx() {
	while (sdGetTimeout(&SD3, TIME_IMMEDIATE) >= 0) {
	}
}

bool waitAck(sysinterval_t timeout) {
	return getByte(timeout) == ACK;
}

bool sendCommand(uint8_t cmd) {
	flushRx();
	const uint8_t frame[2] = { cmd, (uint8_t)~cmd };
	put(frame, sizeof(frame));
	return waitAck(BYTE_TIMEOUT);
}

bool sendAddress(uint32_t address) {
	uint8_t frame[5] = {
		(uint8_t)(address >> 24), (uint8_t)(address >> 16), (uint8_t)(address >> 8), (uint8_t)address, 0
	};
	frame[4] = frame[0] ^ frame[1] ^ frame[2] ^ frame[3];
	put(frame, sizeof(frame));
	return waitAck(BYTE_TIMEOUT);
}

bool sync() {
	const uint8_t syncByte = 0x7F;
	for (int attempt = 0; attempt < 5; attempt++) {
		flushRx();
		put(&syncByte, 1);
		int reply = getByte(TIME_MS2I(100));
		// NACK: the bootloader was already synced and took 0x7F as a bad command; it is listening either way
		if (reply == ACK || reply == NACK) {
			return true;
		}
	}
	return false;
}

// Returns the erase command the bootloader supports (0x43 or 0x44), or -1.
int getEraseCommand() {
	if (!sendCommand(BL_CMD_GET)) {
		return -1;
	}
	int count = getByte(BYTE_TIMEOUT); // number of bytes that follow, minus one: version + command list
	int version = getByte(BYTE_TIMEOUT);
	if (count < 0 || version < 0) {
		return -1;
	}
	int erase = -1;
	for (int i = 0; i < count; i++) {
		int cmd = getByte(BYTE_TIMEOUT);
		if (cmd < 0) {
			return -1;
		}
		if (cmd == BL_CMD_ERASE || cmd == BL_CMD_EXT_ERASE) {
			erase = cmd;
		}
	}
	if (!waitAck(BYTE_TIMEOUT)) {
		return -1;
	}
	efiPrintf("WBO UART: ROM bootloader v%d.%d", version >> 4, version & 0xF);
	return erase;
}

int getProductId() {
	if (!sendCommand(BL_CMD_GET_ID)) {
		return -1;
	}
	int count = getByte(BYTE_TIMEOUT); // 1: two bytes follow
	int hi = getByte(BYTE_TIMEOUT);
	int lo = getByte(BYTE_TIMEOUT);
	if (count != 1 || hi < 0 || lo < 0 || !waitAck(BYTE_TIMEOUT)) {
		return -1;
	}
	return (hi << 8) | lo;
}

bool massErase(int eraseCommand) {
	if (!sendCommand((uint8_t)eraseCommand)) {
		return false;
	}
	if (eraseCommand == BL_CMD_EXT_ERASE) {
		const uint8_t all[3] = { 0xFF, 0xFF, 0x00 };
		put(all, sizeof(all));
	} else {
		const uint8_t all[2] = { 0xFF, 0x00 };
		put(all, sizeof(all));
	}
	return waitAck(ERASE_TIMEOUT);
}

bool writeBlock(uint32_t address, const uint8_t* data, size_t size) {
	if (!sendCommand(BL_CMD_WRITE) || !sendAddress(address)) {
		return false;
	}
	uint8_t length = (uint8_t)(size - 1);
	uint8_t checksum = length;
	for (size_t i = 0; i < size; i++) {
		checksum ^= data[i];
	}
	put(&length, 1);
	put(data, size);
	put(&checksum, 1);
	return waitAck(WRITE_TIMEOUT);
}

bool readBlock(uint32_t address, uint8_t* data, size_t size) {
	if (!sendCommand(BL_CMD_READ) || !sendAddress(address)) {
		return false;
	}
	const uint8_t length[2] = { (uint8_t)(size - 1), (uint8_t)~(size - 1) };
	put(length, sizeof(length));
	if (!waitAck(BYTE_TIMEOUT)) {
		return false;
	}
	for (size_t i = 0; i < size; i++) {
		int b = getByte(BYTE_TIMEOUT);
		if (b < 0) {
			return false;
		}
		data[i] = (uint8_t)b;
	}
	return true;
}

// --- the job ----------------------------------------------------------------------------------------------------

bool fail(const char* status) {
	wboStatus = status;
	efiPrintf("WBO UART: FAILED: %s", status);
	return false;
}

bool flashWideband() {
	const uint8_t* image = wbo_image_start;
	const size_t imageSize = wbo_image_end - wbo_image_start;
	if (imageSize == 0 || imageSize > F042_FLASH_SIZE) {
		return fail("bad wideband image size");
	}
	efiPrintf("WBO UART: %d byte image, entering the F042 ROM bootloader", (int)imageSize);

	setBoot0(true);
	pulseReset(100);

	if (!sync()) {
		return fail("no answer from the F042 bootloader (check U102 power, BOOT0/NRST and the PD8/PD9 link)");
	}
	int pid = getProductId();
	if (pid != F042_PRODUCT_ID) {
		efiPrintf("WBO UART: product ID 0x%x", pid);
		return fail("unexpected product ID (not an STM32F04x)");
	}
	int eraseCommand = getEraseCommand();
	if (eraseCommand < 0) {
		return fail("bootloader command list unreadable or no erase command");
	}

	wboStatus = "erasing";
	if (!massErase(eraseCommand)) {
		return fail("erase refused (read protection set?)");
	}

	wboStatus = "writing";
	uint8_t chunk[WRITE_CHUNK];
	for (size_t offset = 0; offset < imageSize; offset += WRITE_CHUNK) {
		size_t size = std::min(WRITE_CHUNK, imageSize - offset);
		memcpy(chunk, image + offset, size);
		// the bootloader writes whole words: pad the tail with erased-flash bytes
		while (size % 4) {
			chunk[size++] = 0xFF;
		}
		if (!writeBlock(F042_FLASH_BASE + offset, chunk, size)) {
			efiPrintf("WBO UART: write failed at 0x%x", (unsigned int)(F042_FLASH_BASE + offset));
			return fail("write failed");
		}
	}

	wboStatus = "verifying";
	uint8_t readBack[VERIFY_CHUNK];
	for (size_t offset = 0; offset < imageSize; offset += VERIFY_CHUNK) {
		size_t size = std::min(VERIFY_CHUNK, imageSize - offset);
		if (!readBlock(F042_FLASH_BASE + offset, readBack, size)) {
			efiPrintf("WBO UART: read failed at 0x%x", (unsigned int)(F042_FLASH_BASE + offset));
			return fail("read-back failed");
		}
		if (memcmp(readBack, image + offset, size) != 0) {
			efiPrintf("WBO UART: mismatch in block at 0x%x", (unsigned int)(F042_FLASH_BASE + offset));
			return fail("verify mismatch");
		}
	}

	wboStatus = "done: wideband flashed and verified";
	efiPrintf("WBO UART: %s", wboStatus);
	return true;
}

THD_FUNCTION(wboFlashThread, arg) {
	(void)arg;
	chRegSetThreadName("WBO UART flash");

	linkUp();
	flashWideband();
	linkDown();

	// Whatever happened, leave the F042 running from its flash.
	setBoot0(false);
	pulseReset(10);

	wboBusy = false;
}

void printStatus() {
	efiPrintf("WBO UART: %s%s", wboStatus, wboBusy ? " (running)" : "");
}

} // namespace

void initWidebandUartFlash() {
	efiSetPadMode("WBO BOOT0", Gpio::D10, PAL_MODE_OUTPUT_PUSHPULL);
	setBoot0(false);
	efiSetPadMode("WBO NRST", Gpio::D11, PAL_MODE_OUTPUT_OPENDRAIN);
	palSetPad(GPIOD, 11);
	efiSetPadMode("WBO prog TX", Gpio::D8, PAL_MODE_INPUT_PULLUP);
	efiSetPadMode("WBO prog RX", Gpio::D9, PAL_MODE_INPUT_PULLUP);

	addConsoleAction("wbo_uart_flash", startWidebandUartFlash);
	addConsoleAction("wbo_uart_status", printStatus);
}

void startWidebandUartFlash() {
	if (wboBusy) {
		efiPrintf("WBO UART: already running");
		return;
	}
	if (!engine->rpmCalculator.isStopped()) {
		efiPrintf("WBO UART: refused, the engine is turning");
		return;
	}
	wboBusy = true;
	wboStatus = "starting";
	// Just above the idle thread: the serial driver buffers in its interrupt, so a slow thread only slows the job.
	chThdCreateStatic(wboFlashStack, sizeof(wboFlashStack), LOWPRIO + 5, wboFlashThread, nullptr);
}

#else // EFI_BOOTLOADER or simulator

void initWidebandUartFlash() {
}

void startWidebandUartFlash() {
}

#endif
