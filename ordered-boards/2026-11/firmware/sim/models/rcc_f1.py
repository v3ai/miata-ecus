# STM32F103 RCC (0x40021000) for the wideband controller run. Renode's F103 platform only tags RCC_CR with a constant,
# so ChibiOS's clock setup (wait for HSERDY/PLLRDY, then for CFGR.SWS to report the PLL) would spin or read nonsense.
# Ready flags follow their enable bits at once, SWS follows SW, reset flags read as "power-on reset" until cleared.
if request.isInit:
    regs = {0x00: 0x00000083, 0x04: 0, 0x08: 0, 0x0C: 0, 0x10: 0, 0x14: 0x14, 0x18: 0, 0x1C: 0, 0x20: 0, 0x24: 0x0C000000}
elif request.isRead:
    o = request.offset
    v = regs.get(o, 0)
    if o == 0x00:
        # HSIRDY(1) <- HSION(0), HSERDY(17) <- HSEON(16), PLLRDY(25) <- PLLON(24)
        v = (v & ~((1 << 1) | (1 << 17) | (1 << 25))) | ((v & 1) << 1) | ((v >> 16 & 1) << 17) | ((v >> 24 & 1) << 25)
    elif o == 0x04:
        v = (v & ~0xC) | ((v & 3) << 2)
    elif o == 0x20:
        v = (v & ~2) | ((v & 1) << 1)          # LSERDY <- LSEON
    elif o == 0x24:
        v = (v & ~2) | ((v & 1) << 1)          # LSIRDY <- LSION
    request.value = v
elif request.isWrite:
    o = request.offset
    if o == 0x24 and request.value & (1 << 24):  # RMVF clears the reset flags
        regs[o] = request.value & 0x1
    elif o == 0x08:
        regs[o] = request.value & 0x00001F00     # CIR: interrupt enables only; flags never set
    else:
        regs[o] = request.value
