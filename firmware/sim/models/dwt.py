# Cortex-M DWT (0xE0001000): CTRL at 0x00 and the cycle counter CYCCNT at 0x04. ChibiOS and rusEFI use CYCCNT as their
# high-resolution clock (getTimeNowNt, polled delays, the watchdog-reset timer), so it must follow time, not work done:
# on real silicon it keeps counting at the core clock while the CPU sleeps in WFI, where Renode executes no instructions.
# CYCCNT is therefore the machine's virtual time times the core clock (the CPU's PerformanceInMips, set to the
# core clock in MHz in the platform files: 168 for the F407, 48 for the F103), offset by what software last wrote.
if request.isInit:
    ctrl = 0x40000000
    base = 0
    clock = {}
    def now():
        if 'hz' not in clock:
            clock['hz'] = float(self.GetMachine()["sysbus.cpu"].PerformanceInMips) * 1e6
        return int(self.GetMachine().LocalTimeSource.ElapsedVirtualTime.TotalSeconds * clock['hz'])
elif request.isRead:
    if request.offset == 0x04:
        request.value = (now() - base) & 0xFFFFFFFF
    elif request.offset == 0x00:
        request.value = ctrl
    else:
        request.value = 0
elif request.isWrite:
    if request.offset == 0x04:
        base = (now() - request.value) & 0xFFFFFFFF
    elif request.offset == 0x00:
        ctrl = request.value
