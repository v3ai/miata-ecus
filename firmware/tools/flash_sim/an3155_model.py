#!/usr/bin/env python3
"""Model of the STM32F042's ROM serial bootloader (ST AN3155, bootloader ID 0x445) on a pseudo-terminal, plus its
BOOT0 / NRST pins, so the wideband flasher can be exercised without hardware.

Validated against stm32flash (an independent, widely used AN3155 client) before being used on our flasher.

usage: an3155_model.py <link file to write the pty path into> <flash dump out> [options]
  --ctrl FIFO       read "BOOT0=0/1" and "NRST=0/1" lines (pin levels from the main MCU) from this FIFO;
                    without it the chip sits in its bootloader from the start (like a BOOT0 jumper)
  --erase 43|44     which erase command the bootloader advertises (default 44)
  --fault none|silent|rdp|corrupt_read|wrong_pid|nack_write
  --preload FILE    initial flash contents (an already programmed chip)
"""
import argparse
import os
import pty
import select
import sys
import tty

ACK, NACK = 0x79, 0x1F
FLASH_BASE, FLASH_SIZE = 0x08000000, 32 * 1024
PID = 0x445

ap = argparse.ArgumentParser()
ap.add_argument('link')
ap.add_argument('dump')
ap.add_argument('--ctrl')
ap.add_argument('--erase', default='44')
ap.add_argument('--fault', default='none')
ap.add_argument('--preload', help='initial flash contents (an already programmed chip)')
args = ap.parse_args()

master, slave = pty.openpty()
tty.setraw(master)
open(args.link, 'w').write(os.ttyname(slave) + '\n')

flash = bytearray(b'\xff' * FLASH_SIZE)
if args.preload:
    pre = open(args.preload, 'rb').read()
    flash[:len(pre)] = pre
boot0, nrst = (args.ctrl is None), 1
mode = 'bootloader' if args.ctrl is None else 'app'   # app = blank/user code running: ignores the UART
synced = False
stats = {'resets': 0, 'boot_into': [], 'rx_bytes': 0, 'tx_bytes': 0, 'erases': 0, 'writes': 0, 'reads': 0, 'go': 0}
rx = bytearray()
ctrl_fd = os.open(args.ctrl, os.O_RDONLY | os.O_NONBLOCK) if args.ctrl else None
ctrl_buf = b''
log = open(args.dump + '.log', 'w')


def send(*b):
    os.write(master, bytes(b))
    stats['tx_bytes'] += len(b)


def need(n):
    """Block until n bytes have arrived (or the client went away)."""
    global rx
    while len(rx) < n:
        if not pump(5.0):
            raise EOFError
    out, rx = rx[:n], rx[n:]
    return out


def pump(timeout):
    global rx, ctrl_buf
    fds = [master] + ([ctrl_fd] if ctrl_fd is not None else [])
    r, _, _ = select.select(fds, [], [], timeout)
    if not r:
        return False
    if master in r:
        try:
            data = os.read(master, 4096)
        except OSError:
            raise EOFError
        if not data:
            raise EOFError
        stats['rx_bytes'] += len(data)
        if mode == 'bootloader' and args.fault != 'silent':
            rx += data
    if ctrl_fd is not None and ctrl_fd in r:
        data = os.read(ctrl_fd, 4096)
        if not data:                    # the main MCU side closed the pin channel: it is done
            raise EOFError
        ctrl_buf += data
        while b'\n' in ctrl_buf:
            line, ctrl_buf = ctrl_buf.split(b'\n', 1)
            pin_event(line.decode().strip())
    return True


def pin_event(line):
    global boot0, nrst, mode, synced, rx
    name, val = line.split('=')
    val = int(val)
    log.write(f'pin {name}={val}\n')
    if name == 'BOOT0':
        boot0 = val
    elif name == 'NRST':
        if nrst == 0 and val == 1:          # reset released: sample BOOT0
            stats['resets'] += 1
            # F04x: BOOT0 high -> system memory; low -> main flash (the F04x bootloader also jumps to flash once it
            # is no longer empty, ST "Empty check mechanism on STM32", so a blank chip stays in the bootloader)
            blank = flash[:4] == b'\xff\xff\xff\xff'
            mode = 'bootloader' if (boot0 or blank) else 'app'
            stats['boot_into'].append(mode)
            synced = False
            rx = bytearray()
        nrst = val


def addr_ok(a, n):
    return FLASH_BASE <= a and a + n <= FLASH_BASE + FLASH_SIZE


def read_addr():
    b = need(5)
    if b[4] != (b[0] ^ b[1] ^ b[2] ^ b[3]):
        return None
    return int.from_bytes(b[:4], 'big')


def serve():
    global synced, mode
    while True:
        if not synced:
            b = need(1)[0]
            if b == 0x7F:
                synced = True
                send(ACK)
            continue
        cmd, comp = need(2)
        if cmd ^ comp != 0xFF:
            send(NACK)
            continue
        if cmd == 0x00:                          # Get
            cmds = [0x00, 0x01, 0x02, 0x11, 0x21, 0x31, int(args.erase, 16), 0x63, 0x73, 0x82, 0x92]
            send(ACK, len(cmds), 0x31, *cmds, ACK)
        elif cmd == 0x01:                        # Get version and read protection status
            send(ACK, 0x31, 0x00, 0x00, ACK)
        elif cmd == 0x02:                        # Get ID
            pid = 0x444 if args.fault == 'wrong_pid' else PID
            send(ACK, 1, pid >> 8, pid & 0xFF, ACK)
        elif cmd == 0x11:                        # Read memory
            if args.fault == 'rdp':
                send(NACK)
                continue
            send(ACK)
            a = read_addr()
            if a is None:
                send(NACK)
                continue
            send(ACK)
            n, nc = need(2)
            if n ^ nc != 0xFF or not addr_ok(a, n + 1):
                send(NACK)
                continue
            data = bytearray(flash[a - FLASH_BASE:a - FLASH_BASE + n + 1])
            if args.fault == 'corrupt_read' and a - FLASH_BASE <= 0x1000 < a - FLASH_BASE + n + 1:
                data[0x1000 - (a - FLASH_BASE)] ^= 0x40
            send(ACK, *data)
            stats['reads'] += 1
        elif cmd == 0x21:                        # Go
            send(ACK)
            a = read_addr()
            if a is None:
                send(NACK)
                continue
            send(ACK)
            stats['go'] += 1
            mode = 'app'
            synced = False
        elif cmd == 0x31:                        # Write memory
            if args.fault == 'rdp':
                send(NACK)
                continue
            send(ACK)
            a = read_addr()
            if a is None or a % 4:
                send(NACK)
                continue
            send(ACK)
            n = need(1)[0] + 1
            data = need(n)
            cs = need(1)[0]
            x = n - 1
            for v in data:
                x ^= v
            if x != cs or n % 4 or not addr_ok(a, n) or args.fault == 'nack_write':
                send(NACK)
                continue
            off = a - FLASH_BASE
            # flash can only clear bits: model a real NOR flash (programming over non-erased data corrupts)
            for i, v in enumerate(data):
                flash[off + i] &= v
            stats['writes'] += 1
            send(ACK)
        elif cmd in (0x43, 0x44):                # Erase / Extended erase
            if cmd != int(args.erase, 16) or args.fault == 'rdp':
                send(NACK)
                continue
            send(ACK)
            if cmd == 0x43:
                n = need(1)[0]
                if n == 0xFF:
                    need(1)                      # checksum 0x00
                    flash[:] = b'\xff' * FLASH_SIZE
                else:
                    pages = need(n + 2)
                    for p in pages[:-1]:
                        flash[p * 1024:(p + 1) * 1024] = b'\xff' * 1024
            else:
                hi, lo = need(2)
                n = (hi << 8) | lo
                if n == 0xFFFF:
                    need(1)
                    flash[:] = b'\xff' * FLASH_SIZE
                else:
                    raw = need(2 * (n + 1) + 1)
                    for k in range(n + 1):
                        p = (raw[2 * k] << 8) | raw[2 * k + 1]
                        flash[p * 1024:(p + 1) * 1024] = b'\xff' * 1024
            stats['erases'] += 1
            send(ACK)
        else:
            send(NACK)


try:
    serve()
except EOFError:
    pass
open(args.dump, 'wb').write(flash)
log.write(f'final BOOT0={boot0} NRST={nrst} mode={mode}\n{stats}\n')
log.close()
