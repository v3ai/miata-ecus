// Bus front for Renode's NVIC/SCB block (0xE000E000-0xE000EFFF) that adds ICSR.RETTOBASE, which Renode 1.15's NVIC
// never sets. ChibiOS's ARMv7-M port reschedules on interrupt exit only when RETTOBASE (bit 11) says the running
// exception is the only active one; without it a thread woken by an interrupt never runs.
//
// The NVIC itself is declared in the platform file without a bus address (the CPU and the interrupt lines still
// reach it directly); this peripheral sits at its address, forwards every access, and on ICSR reads sets bit 11
// exactly when the NVIC's own stack of active exceptions holds one entry, which is the hardware definition.
// (An earlier version used CPU hooks at every handler entry; a hook hit costs milliseconds of host time in Renode,
// and at rusEFI's tens of thousands of interrupts per second that made the emulation 100x slower.)
using System;
using System.Collections.Generic;
using System.Reflection;
using Antmicro.Renode.Core;
using Antmicro.Renode.Peripherals.Bus;
using Antmicro.Renode.Peripherals.IRQControllers;

namespace Antmicro.Renode.Peripherals.Miata
{
    [AllowedTranslations(AllowedTranslation.ByteToDoubleWord | AllowedTranslation.WordToDoubleWord)]
    public class NvicRettobase : IDoubleWordPeripheral, IKnownSize
    {
        public NvicRettobase(IMachine machine, NVIC nvic)
        {
            this.nvic = nvic;
            var field = typeof(NVIC).GetField("activeIRQs", BindingFlags.NonPublic | BindingFlags.Instance);
            active = (Stack<int>)field.GetValue(nvic);
        }

        public long Size => 0x1000;
        public ulong IcsrReads { get; private set; }
        public ulong RettobaseSet { get; private set; }

        public uint ReadDoubleWord(long offset)
        {
            var v = nvic.ReadDoubleWord(offset);
            if(offset == 0xD04)
            {
                IcsrReads++;
                if(active.Count == 1)
                {
                    v |= 1u << 11;
                    RettobaseSet++;
                }
                else
                {
                    v &= ~(1u << 11);
                }
            }
            return v;
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            nvic.WriteDoubleWord(offset, value);
        }

        public void Reset()
        {
        }

        private readonly NVIC nvic;
        private readonly Stack<int> active;
    }
}
