// Runs the board's wideband flasher (wideband_uart_flash.cpp, unmodified) against an3155_model.py.
// usage: host_flasher <pty path> <ctrl fifo> [engine_running]
#include "pch.h"
#include "wideband_uart_flash.h"
#include <fcntl.h>
#include <termios.h>

SerialDriver SD3;
FILE* g_ctrl;
int g_pinLevel[16];
const SerialConfig* g_lastConfig;
long g_txBytes, g_rxBytes;
GPIO_TypeDef gpiod;
static Engine eng;
Engine* engine = &eng;

int main(int argc, char** argv) {
	SD3.fd = open(argv[1], O_RDWR | O_NOCTTY);
	struct termios t;
	tcgetattr(SD3.fd, &t);
	cfmakeraw(&t);
	tcsetattr(SD3.fd, TCSANOW, &t);
	g_ctrl = fopen(argv[2], "w");
	eng.rpmCalculator.stopped = argc < 4;
	auto t0 = std::chrono::steady_clock::now();
	initWidebandUartFlash();       // boot: BOOT0 low, NRST released
	startWidebandUartFlash();      // what wbo_uart_flash / the TunerStudio button does
	double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
	printf("RESULT tx=%ld rx=%ld boot0=%d nrst=%d baud=%u cr1=0x%x seconds=%.2f\n", g_txBytes, g_rxBytes,
		g_pinLevel[10], g_pinLevel[11], g_lastConfig ? g_lastConfig->speed : 0, g_lastConfig ? g_lastConfig->cr1 : 0, s);
	fclose(g_ctrl);
	return 0;
}
