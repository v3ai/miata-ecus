/**
 * Host shim: just enough of rusEFI / ChibiOS for firmware/board/wideband_uart_flash.cpp to compile and run on a PC.
 * The USART is a pseudo-terminal served by an3155_model.py; BOOT0 (PD10) and NRST (PD11) levels are written as text
 * lines to a FIFO the model reads. Everything the flasher does on the wire goes through these few functions.
 */
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdarg>
#include <algorithm>
#include <chrono>
#include <thread>
#include <poll.h>
#include <unistd.h>

#define EFI_PROD_CODE 1
#define STM32_SERIAL_USE_USART3 1
#define USART_CR1_M (1u << 12)
#define USART_CR1_PCE (1u << 10)

typedef int32_t msg_t;
typedef uint32_t sysinterval_t;
#define TIME_IMMEDIATE ((sysinterval_t)0)
#define TIME_MS2I(ms) ((sysinterval_t)(ms))
#define LOWPRIO 1

struct SerialConfig { uint32_t speed; uint16_t cr1; uint16_t cr2; uint16_t cr3; };
struct SerialDriver { int fd; const SerialConfig* cfg; };
extern SerialDriver SD3;
extern FILE* g_ctrl;
extern int g_pinLevel[16];
extern const SerialConfig* g_lastConfig;
extern long g_txBytes, g_rxBytes;

inline void sdStart(SerialDriver* sd, const SerialConfig* cfg) { sd->cfg = cfg; g_lastConfig = cfg; }
inline void sdStop(SerialDriver*) {}
inline msg_t sdGetTimeout(SerialDriver* sd, sysinterval_t ms) {
	struct pollfd p = {sd->fd, POLLIN, 0};
	if (poll(&p, 1, (int)ms) <= 0) {
		return -1; // MSG_TIMEOUT
	}
	uint8_t b;
	if (read(sd->fd, &b, 1) != 1) {
		return -1;
	}
	g_rxBytes++;
	return b;
}
inline size_t sdWrite(SerialDriver* sd, const uint8_t* buf, size_t n) {
	g_txBytes += n;
	return (size_t)write(sd->fd, buf, n);
}

// GPIO: only port D is used. Pin changes on PD10/PD11 are reported to the model.
struct GPIO_TypeDef { int port; };
extern GPIO_TypeDef gpiod;
#define GPIOD (&gpiod)
#define PAL_HIGH 1
#define PAL_LOW 0
#define PAL_MODE_ALTERNATE(n) (0x100 | (n))
#define PAL_STM32_PUPDR_PULLUP 0x1000
#define PAL_MODE_INPUT_PULLUP 0x2000
#define PAL_MODE_OUTPUT_PUSHPULL 0x4000
#define PAL_MODE_OUTPUT_OPENDRAIN 0x8000
inline void reportPin(int pad, int v) {
	g_pinLevel[pad] = v;
	if (g_ctrl && (pad == 10 || pad == 11)) {
		fprintf(g_ctrl, "%s=%d\n", pad == 10 ? "BOOT0" : "NRST", v);
		fflush(g_ctrl);
	}
}
inline void palWritePad(GPIO_TypeDef*, int pad, int v) { reportPin(pad, v); }
inline void palSetPad(GPIO_TypeDef*, int pad) { reportPin(pad, 1); }
inline void palClearPad(GPIO_TypeDef*, int pad) { reportPin(pad, 0); }
inline void palSetPadMode(GPIO_TypeDef*, int, int) {}

enum class Gpio { D8, D9, D10, D11 };
inline void efiSetPadMode(const char*, Gpio, int) {}

// Threads run synchronously on the host; sleeps are real so the model sees realistic pin timing.
#define THD_WORKING_AREA(name, size) char name[size]
#define THD_FUNCTION(name, arg) void name(void* arg)
inline void chThdCreateStatic(void*, size_t, int, void (*fn)(void*), void* arg) { fn(arg); }
inline void chThdSleepMilliseconds(int ms) { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); }
inline void chRegSetThreadName(const char*) {}

inline void efiPrintf(const char* fmt, ...) {
	va_list ap;
	va_start(ap, fmt);
	vprintf(fmt, ap);
	va_end(ap);
	printf("\n");
	fflush(stdout);
}
typedef void (*Void)();
inline void addConsoleAction(const char*, Void) {}

struct RpmCalculator { bool stopped = true; bool isStopped() const { return stopped; } };
struct Engine { RpmCalculator rpmCalculator; };
extern Engine* engine;
