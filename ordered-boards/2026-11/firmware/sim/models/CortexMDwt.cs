// Cortex-M DWT (0xE0001000): CTRL at 0x00 and the cycle counter CYCCNT at 0x04. ChibiOS and rusEFI read CYCCNT as
// their high-resolution clock (getTimeNowNt, polled delays, kernel statistics on every interrupt), so it must follow
// time, not work done: on silicon it keeps counting while the CPU sleeps in WFI, where Renode executes no
// instructions. CYCCNT = virtual time x core clock, offset by what software last wrote. Renode 1.15 has no DWT.
// (C#, not a Python peripheral: the firmware reads it about 10^5 times per second.)
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Peripherals.Bus;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class CortexMDwt : IDoubleWordPeripheral, IKnownSize
    {
        public CortexMDwt(IMachine machine, long coreClock)
        {
            this.machine = machine;
            this.hz = coreClock;
            Reset();
        }

        public long Size => 0x1000;

        public void Reset()
        {
            ctrl = 0x40000000; // NUMCOMP = 4
            offset = 0;
        }

        public uint ReadDoubleWord(long reg)
        {
            switch(reg)
            {
            case 0x00: return ctrl;
            case 0x04: return (uint)(Now() - offset);
            }
            return 0;
        }

        public void WriteDoubleWord(long reg, uint value)
        {
            switch(reg)
            {
            case 0x00: ctrl = value; break;
            case 0x04: offset = Now() - value; break;
            }
        }

        private ulong Now()
        {
            return (ulong)(machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds * hz);
        }

        private readonly IMachine machine;
        private readonly long hz;
        private uint ctrl;
        private ulong offset;
    }
}
