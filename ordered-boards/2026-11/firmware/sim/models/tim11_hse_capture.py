# TIM11 on the STM32F407 as rusEFI's HSE auto-detection (osc_detector.cpp) uses it: input capture on channel 1 of
# HSE/RTCPRE (31), timer clock TIMCLK2 = 168 MHz. Every read of SR shows CC1IF; every read of CCR1 returns the next
# capture, 31 * 168 MHz / 8 MHz = 651 counts after the previous one (an 8 MHz crystal, board Y1).
# Other registers are plain storage.
if request.isInit:
    regs = {}
    capture = 0
    STEP = int(round(31 * 168e6 / 8e6))
elif request.isRead:
    if request.offset == 0x10:          # SR
        request.value = 0x2             # CC1IF
    elif request.offset == 0x34:        # CCR1
        capture = (capture + STEP) & 0xFFFF
        request.value = capture
    else:
        request.value = regs.get(request.offset, 0)
elif request.isWrite:
    regs[request.offset] = request.value
