# STM32F4 PWR (RM0090 5.4): CR at 0x00, CSR at 0x04. Status bits follow their enables at once: backup regulator
# ready (BRR, bit 3) follows BRE (bit 9); voltage-scaling ready (VOSRDY, bit 14) is always set.
if request.isInit:
    cr = 0x0000C000
    csr = 0
elif request.isRead:
    if request.offset == 0x00:
        request.value = cr
    elif request.offset == 0x04:
        v = csr | (1 << 14)
        if csr & (1 << 9):
            v |= 1 << 3
        request.value = v
    else:
        request.value = 0
elif request.isWrite:
    if request.offset == 0x00:
        cr = request.value
    elif request.offset == 0x04:
        csr = request.value & ((1 << 8) | (1 << 9))     # EWUP, BRE writable
