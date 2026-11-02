// Listens on a Renode CAN hub and writes every frame with its virtual time, for the firmware-in-the-loop analysis of
// the ECU <-> wideband bus. Renode's CAN hub passes frames without bit timing, so the sniffer also reports the bit
// rate each controller is set to (BTR and its APB1 clock), which is what decides whether two real controllers can
// talk: CheckBitTiming "ecu" 0x40006800 42000000 "wbo" 0x40006400 24000000.
// Output lines: "<time ns> <id hex> <x|s> <data hex>" (x = 29-bit identifier, s = 11-bit). The identifier is decoded
// from the bxCAN register layout Renode's STMCAN passes on.
using System;
using System.IO;
using Antmicro.Renode.Core;
using Antmicro.Renode.Core.CAN;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.CAN;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class CanSniffer : ICAN, Antmicro.Renode.Peripherals.Bus.IDoubleWordPeripheral, IKnownSize
    {
        public CanSniffer(IMachine machine)
        {
            this.machine = machine;
        }

        public event Action<CANMessageFrame> FrameSent;

        public ulong Frames { get; private set; }

        public void SetOutputFile(string path)
        {
            writer?.Dispose();
            writer = new StreamWriter(path, false) { AutoFlush = true };
        }

        public void OnFrameReceived(CANMessageFrame message)
        {
            Frames++;
            if(writer == null)
            {
                return;
            }
            var ns = (long)Math.Round(machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds * 1e9);
            // Renode's bxCAN model hands the hub the raw CAN_TIxR value: IDE is bit 2, the identifier is in bits 3-31
            // (29-bit) or 21-31 (11-bit)
            var raw = message.Id;
            var ext = (raw & 4) != 0;
            var id = ext ? raw >> 3 : raw >> 21;
            writer.WriteLine("{0} {1:X} {2} {3}", ns, id, ext ? "x" : "s",
                BitConverter.ToString(message.Data ?? new byte[0]).Replace("-", ""));
        }

        // Bit rate (bit/s) and sample point of a bxCAN controller in another machine
        public string BitTiming(string machineName, ulong canBase, long apb1)
        {
            if(!EmulationManager.Instance.CurrentEmulation.TryGetMachineByName(machineName, out var m))
            {
                return "no machine " + machineName;
            }
            // Renode's STMCAN returns BTR only while the controller is in init mode (silicon: always readable), so
            // take the stored value from the model itself
            uint btr;
            try
            {
                var flags = System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public |
                    System.Reflection.BindingFlags.Instance;
                var can = m.SystemBus.WhatIsAt(canBase).Peripheral;
                var regs = can.GetType().GetField("registers", flags).GetValue(can);
                var reg = regs.GetType().GetField("CAN_BTR", flags).GetValue(regs);
                btr = (uint)reg.GetType().GetField("RegValue", flags).GetValue(reg);
            }
            catch(Exception e)
            {
                this.Log(LogLevel.Error, "CANTIMING {0}: BTR not readable ({1})", machineName, e.Message);
                return "BTR not readable";
            }
            var brp = (btr & 0x3FF) + 1;
            var ts1 = ((btr >> 16) & 0xF) + 1;
            var ts2 = ((btr >> 20) & 0x7) + 1;
            var sjw = ((btr >> 24) & 0x3) + 1;
            var tq = 1 + ts1 + ts2;
            var rate = (double)apb1 / (brp * tq);
            var silent = (btr & (1u << 31)) != 0;
            var loop = (btr & (1u << 30)) != 0;
            var s = string.Format("{0} BTR=0x{1:X8} bitrate={2:F0} sample={3:F1}% tq={4} sjw={5}{6}{7}", machineName, btr, rate,
                100.0 * (1 + ts1) / tq, tq, sjw, silent ? " SILENT" : "", loop ? " LOOPBACK" : "");
            this.Log(LogLevel.Error, "CANTIMING " + s);
            return s;
        }

        public void Reset()
        {
        }

        private readonly IMachine machine;
        private StreamWriter writer;

        // Bus presence only (Renode creates a peripheral declared in a platform file only when it is registered or
        // connected); the registers read as 0.
        public long Size => 0x100;
        public uint ReadDoubleWord(long offset) { return 0; }
        public void WriteDoubleWord(long offset, uint value) { }
    }
}
