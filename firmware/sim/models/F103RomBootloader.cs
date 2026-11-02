// The STM32F103's system-memory (ROM) USART bootloader as the ECU sees it, for the firmware-in-the-loop run of the
// ECU's wideband flasher (firmware/board/wideband_uart_flash.cpp). ST's ROM code is not available, so its protocol
// (ST AN3155, bootloader version 2.2 as on STM32F10xxx medium density, AN2606) is modelled here and acts on the
// second emulated machine, the F103 itself:
//  - Inputs: GPIO 0 = BOOT0 (ECU PD10), GPIO 1 = NRST (ECU PD11, open drain, low = reset). A rising NRST with BOOT0
//    high halts the F103's CPU and starts the bootloader; with BOOT0 low the F103 machine is reset and runs its flash.
//  - Serial: the ECU's USART3 (constructor argument `host`). The bootloader answers only if that USART is set to what
//    the ROM accepts: 8 data bits + even parity (M = 1, PCE = 1, PS = 0), one stop bit, 1200-115200 baud. Bytes go
//    back at the configured baud rate, so the ECU's receive path sees real timing.
//  - Commands: Get, Get Version, Get ID (0x410), Read Memory, Go, Write Memory, Erase (0x43, global and page),
//    Write Protect/Unprotect and Readout Protect/Unprotect are listed but answered with NACK.
//  - Writes go into the F103 machine's memory. Writing flash that is not erased is refused with NACK (on silicon it
//    sets PGERR and the content is not what was sent), as is a write whose length is not a multiple of 4.
//  - Timing: page erase 20 ms, mass erase 30 ms, 52.5 us per programmed half-word (STM32F103 datasheet tERASE/tME/
//    tPROG typical values).
using System;
using System.Collections.Generic;
using System.Linq;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.CPU;
using Antmicro.Renode.Peripherals.Timers;
using Antmicro.Renode.Peripherals.UART;
using Antmicro.Renode.Time;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class F103RomBootloader : IGPIOReceiver, Antmicro.Renode.Peripherals.Bus.IDoubleWordPeripheral, IKnownSize
    {
        public F103RomBootloader(IMachine machine, IUART host, string targetMachine = "wbo", long hostApb1 = 42000000,
            ulong hostUsartBase = 0x40004800)
        {
            this.machine = machine;
            this.host = host;
            this.targetName = targetMachine;
            this.hostApb1 = hostApb1;
            this.hostUsartBase = hostUsartBase;
            host.CharReceived += OnHostByte;
            // Renode's STM32_UART does not store CR1.M (word length) and reads it back as 0, so the frame check uses
            // the value the firmware last wrote to CR1
            machine.SystemBus.AddWatchpointHook(hostUsartBase + 0x0C, Antmicro.Renode.Peripherals.Bus.SysbusAccessWidth.DoubleWord,
                Antmicro.Renode.Peripherals.Bus.Access.Write, (cpu, address, width, value) => { hostCr1 = (uint)value; });
            txTimer = new LimitTimer(machine.ClockSource, 1000000, this, "bl-tx", limit: 100, direction: Direction.Ascending,
                enabled: false, workMode: WorkMode.OneShot, eventEnabled: true);
            txTimer.LimitReached += SendNext;
            busyTimer = new LimitTimer(machine.ClockSource, 1000000, this, "bl-busy", limit: 100, direction: Direction.Ascending,
                enabled: false, workMode: WorkMode.OneShot, eventEnabled: true);
            busyTimer.LimitReached += BusyDone;
        }

        public bool Active { get; private set; }
        public string LastEvent { get; private set; } = "none";
        public ulong BytesWritten { get; private set; }
        public ulong Erases { get; private set; }
        public ulong Nacks { get; private set; }
        public bool Boot0 { get; private set; }
        public bool Nrst { get; private set; } = true;

        public void OnGPIO(int number, bool value)
        {
            if(number == 0)
            {
                Boot0 = value;
                return;
            }
            if(number != 1 || value == Nrst)
            {
                return;
            }
            Nrst = value;
            var target = Target();
            if(target == null)
            {
                return;
            }
            if(!value)
            {
                // held in reset
                foreach(var c in target.SystemBus.GetCPUs())
                {
                    c.IsHalted = true;
                }
                Active = false;
                return;
            }
            if(Boot0)
            {
                target.RequestResetInSafeState(() =>
                {
                    foreach(var c in target.SystemBus.GetCPUs())
                    {
                        c.IsHalted = true;
                    }
                });
                Enter();
            }
            else
            {
                Active = false;
                target.RequestResetInSafeState(() =>
                {
                    foreach(var c in target.SystemBus.GetCPUs())
                    {
                        c.IsHalted = false;
                    }
                });
                Note("F103 reset with BOOT0 low: running from flash");
            }
        }

        // CRC-32 (zlib) of the first `length` bytes of the F103's flash, to compare with the image the ECU carries
        public string FlashCrc(int length)
        {
            var t = Target();
            uint crc = 0xFFFFFFFF;
            for(var i = 0; i < length; i++)
            {
                crc ^= t.SystemBus.ReadByte(FlashBase + (ulong)i);
                for(var k = 0; k < 8; k++)
                {
                    crc = (crc >> 1) ^ (0xEDB88320u & (uint)-(int)(crc & 1));
                }
            }
            var r = string.Format("{0:x8}", ~crc);
            this.Log(LogLevel.Error, "FLASHCRC {0} {1}", length, r);
            return r;
        }

        public void Reset()
        {
            Active = false;
            rx.Clear();
            tx.Clear();
        }

        private IMachine Target()
        {
            if(target == null && !EmulationManager.Instance.CurrentEmulation.TryGetMachineByName(targetName, out target))
            {
                this.Log(LogLevel.Error, "no machine named '{0}' for the F103 bootloader", targetName);
            }
            return target;
        }

        private void Enter()
        {
            Active = true;
            synced = false;
            rx.Clear();
            tx.Clear();
            state = State.WaitSync;
            Note("F103 reset with BOOT0 high: system-memory bootloader running");
        }

        private void Note(string what)
        {
            LastEvent = what;
            this.Log(LogLevel.Info, what);
        }

        private bool HostFrameOk(out double baud)
        {
            var brr = machine.SystemBus.ReadDoubleWord(hostUsartBase + 0x08);
            var cr1 = hostCr1 ?? machine.SystemBus.ReadDoubleWord(hostUsartBase + 0x0C);
            var cr2 = machine.SystemBus.ReadDoubleWord(hostUsartBase + 0x10);
            var over8 = (cr1 & (1u << 15)) != 0;
            // OVER8 = 0: baud = f / BRR. OVER8 = 1: USARTDIV = BRR[15:4] + BRR[2:0] / 8, baud = f / (8 USARTDIV)
            var div = over8 ? ((brr >> 4) & 0xFFF) + (brr & 7) / 8.0 : brr;
            baud = div == 0 ? 0 : hostApb1 / ((over8 ? 8.0 : 16.0) * (over8 ? div : div / 16.0));
            var m = (cr1 & (1u << 12)) != 0;
            var pce = (cr1 & (1u << 10)) != 0;
            var ps = (cr1 & (1u << 9)) != 0;
            var stop = (cr2 >> 12) & 3;
            var ok = m && pce && !ps && stop == 0 && baud >= 1200 * 0.97 && baud <= 115200 * 1.03;
            if(!ok && !reportedFrame)
            {
                reportedFrame = true;
                this.Log(LogLevel.Error, "host USART frame not accepted by the ROM bootloader: CR1=0x{0:X} (M={1} PCE={2} PS={3}) stop={4} baud={5:F0}",
                    cr1, m, pce, ps, stop, baud);
                LastEvent = "host serial settings rejected";
            }
            hostBaud = baud;
            return ok;
        }

        private void OnHostByte(byte b)
        {
            if(!Active)
            {
                return;
            }
            if(!HostFrameOk(out var _))
            {
                return; // garbage on the line as far as the ROM code is concerned
            }
            if(busy)
            {
                // the ROM code is busy erasing/writing and is not reading the USART: overrun, byte lost
                this.Log(LogLevel.Warning, "byte 0x{0:X2} sent while the bootloader was busy: lost", b);
                return;
            }
            rx.Add(b);
            Process();
        }

        private void Send(params byte[] bytes)
        {
            foreach(var b in bytes)
            {
                tx.Enqueue(b);
            }
            if(!txTimer.Enabled)
            {
                ScheduleTx();
            }
        }

        private void Ack() { Send(ACK); }

        private void Nack()
        {
            Nacks++;
            Send(NACK);
        }

        private void ScheduleTx()
        {
            if(tx.Count == 0)
            {
                return;
            }
            var us = (ulong)Math.Max(1, Math.Round(11 * 1e6 / (hostBaud > 0 ? hostBaud : 115200)));
            txTimer.Value = 0;
            txTimer.Limit = us;
            txTimer.Enabled = true;
        }

        private void SendNext()
        {
            if(tx.Count > 0)
            {
                host.WriteChar(tx.Dequeue());
            }
            ScheduleTx();
        }

        private void After(double seconds, Action then)
        {
            busy = true;
            afterBusy = then;
            busyTimer.Value = 0;
            busyTimer.Limit = (ulong)Math.Max(1, Math.Round(seconds * 1e6));
            busyTimer.Enabled = true;
        }

        private void BusyDone()
        {
            busy = false;
            var a = afterBusy;
            afterBusy = null;
            a?.Invoke();
        }

        private static byte Xor(IEnumerable<byte> bytes)
        {
            byte x = 0;
            foreach(var b in bytes)
            {
                x ^= b;
            }
            return x;
        }

        private bool AddressOk(uint a, uint len)
        {
            return (a >= FlashBase && a + len <= FlashBase + FlashSize) || (a >= 0x20000800 && a + len <= 0x20005000)
                || (a >= 0x1FFFF000 && a + len <= 0x1FFFF810);
        }

        private void Process()
        {
            switch(state)
            {
            case State.WaitSync:
                if(rx[0] == 0x7F)
                {
                    synced = true;
                    state = State.Command;
                    Note("synchronised (0x7F)");
                    Ack();
                }
                rx.Clear();
                return;
            case State.Command:
                if(rx.Count == 1 && rx[0] == 0x7F && synced)
                {
                    // a second 0x7F is taken as a command byte without its complement
                    return;
                }
                if(rx.Count < 2)
                {
                    return;
                }
                var cmd = rx[0];
                var ok = (byte)~rx[0] == rx[1];
                rx.Clear();
                if(!ok)
                {
                    Nack();
                    return;
                }
                Command(cmd);
                return;
            case State.Address:
                if(rx.Count < 5)
                {
                    return;
                }
                var addr = (uint)(rx[0] << 24 | rx[1] << 16 | rx[2] << 8 | rx[3]);
                var good = Xor(rx.Take(4)) == rx[4];
                rx.Clear();
                if(!good || !AddressOk(addr, 1))
                {
                    state = State.Command;
                    Nack();
                    return;
                }
                address = addr;
                Ack();
                if(pending == 0x21)
                {
                    Go();
                    return;
                }
                state = pending == 0x11 ? State.ReadCount : State.WriteData;
                return;
            case State.ReadCount:
                if(rx.Count < 2)
                {
                    return;
                }
                var n = rx[0];
                var nok = (byte)~rx[0] == rx[1];
                rx.Clear();
                state = State.Command;
                if(!nok || !AddressOk(address, (uint)n + 1))
                {
                    Nack();
                    return;
                }
                Ack();
                var bus = Target().SystemBus;
                var data = new byte[n + 1];
                for(var i = 0; i <= n; i++)
                {
                    data[i] = bus.ReadByte(address + (ulong)i);
                }
                Send(data);
                return;
            case State.WriteData:
                if(rx.Count < 1 || rx.Count < rx[0] + 3)
                {
                    return;
                }
                var count = rx[0] + 1;
                var payload = rx.Skip(1).Take(count).ToArray();
                var sumOk = Xor(rx.Take(count + 1)) == rx[count + 1];
                rx.Clear();
                state = State.Command;
                if(!sumOk || count % 4 != 0 || !AddressOk(address, (uint)count))
                {
                    Nack();
                    return;
                }
                var tbus = Target().SystemBus;
                var flash = address >= FlashBase && address < FlashBase + FlashSize;
                if(flash)
                {
                    for(var i = 0; i < count; i++)
                    {
                        if(tbus.ReadByte(address + (ulong)i) != 0xFF && payload[i] != tbus.ReadByte(address + (ulong)i))
                        {
                            this.Log(LogLevel.Error, "write to flash at 0x{0:X8} that is not erased: refused", address + (ulong)i);
                            Nack();
                            return;
                        }
                    }
                }
                for(var i = 0; i < count; i++)
                {
                    tbus.WriteByte(address + (ulong)i, payload[i]);
                }
                BytesWritten += (ulong)count;
                After(flash ? count / 2 * 52.5e-6 : 10e-6, Ack);
                return;
            case State.EraseCount:
                if(rx.Count < 2)
                {
                    return;
                }
                if(rx[0] == 0xFF)
                {
                    var gok = rx[1] == 0x00;
                    rx.Clear();
                    state = State.Command;
                    if(!gok)
                    {
                        Nack();
                        return;
                    }
                    var eb = Target().SystemBus;
                    for(ulong a = 0; a < FlashSize; a += 4)
                    {
                        eb.WriteDoubleWord(FlashBase + a, 0xFFFFFFFF);
                    }
                    Erases++;
                    Note("global erase");
                    After(0.030, Ack);
                    return;
                }
                var pages = rx[0] + 1;
                if(rx.Count < pages + 2)
                {
                    return;
                }
                var list = rx.Skip(1).Take(pages).ToArray();
                var pok = Xor(rx.Take(pages + 1)) == rx[pages + 1];
                rx.Clear();
                state = State.Command;
                if(!pok || list.Any(p => p >= FlashSize / PageSize))
                {
                    Nack();
                    return;
                }
                var pb = Target().SystemBus;
                foreach(var p in list)
                {
                    for(ulong a = 0; a < PageSize; a += 4)
                    {
                        pb.WriteDoubleWord(FlashBase + (ulong)p * PageSize + a, 0xFFFFFFFF);
                    }
                }
                Erases++;
                After(0.020 * pages, Ack);
                return;
            }
        }

        private void Command(byte cmd)
        {
            switch(cmd)
            {
            case 0x00:
                Ack();
                Send(11, 0x22, 0x00, 0x01, 0x02, 0x11, 0x21, 0x31, 0x43, 0x63, 0x73, 0x82, 0x92);
                Ack();
                break;
            case 0x01:
                Ack();
                Send(0x22, 0x00, 0x00);
                Ack();
                break;
            case 0x02:
                Ack();
                Send(0x01, 0x04, 0x10);
                Ack();
                break;
            case 0x11:
            case 0x21:
            case 0x31:
                pending = cmd;
                state = State.Address;
                Ack();
                break;
            case 0x43:
                state = State.EraseCount;
                Ack();
                break;
            default:
                // 0x44 (extended erase) is not in this bootloader version; protection commands are not modelled
                Nack();
                break;
            }
        }

        private void Go()
        {
            var t = Target();
            var sp = t.SystemBus.ReadDoubleWord(address);
            var pc = t.SystemBus.ReadDoubleWord(address + 4);
            Active = false;
            state = State.Command;
            Note(string.Format("Go 0x{0:X8}: SP 0x{1:X8}, PC 0x{2:X8}", address, sp, pc));
            foreach(var c in t.SystemBus.GetCPUs())
            {
                var cpu = c as ICPUWithRegisters;
                if(cpu != null)
                {
                    cpu.SetRegister(13, sp);
                    cpu.PC = pc & ~1u;
                }
                c.IsHalted = false;
            }
        }

        private enum State { WaitSync, Command, Address, ReadCount, WriteData, EraseCount }

        private const byte ACK = 0x79;
        private const byte NACK = 0x1F;
        private const ulong FlashBase = 0x08000000;
        private const ulong FlashSize = 0x10000;
        private const ulong PageSize = 0x400;
        private readonly IMachine machine;
        private readonly IUART host;
        private readonly string targetName;
        private readonly long hostApb1;
        private readonly ulong hostUsartBase;
        private readonly LimitTimer txTimer;
        private readonly LimitTimer busyTimer;
        private readonly List<byte> rx = new List<byte>();
        private readonly Queue<byte> tx = new Queue<byte>();
        private IMachine target;
        private State state;
        private bool synced;
        private bool busy;
        private bool reportedFrame;
        private double hostBaud;
        private uint? hostCr1;
        private Action afterBusy;
        private byte pending;
        private uint address;

        // Bus presence only (Renode creates a peripheral declared in a platform file only when it is registered or
        // connected); the registers read as 0.
        public long Size => 0x100;
        public uint ReadDoubleWord(long offset) { return 0; }
        public void WriteDoubleWord(long offset, uint value) { }
    }
}
