// Bus front for a Renode STM32_Timer whose compare channels must match at counter value 0. Renode 1.15's STM32_Timer
// never matches a compare value of 0 (it disables the channel, and re-enables it only while CNT < CCR), whereas on
// silicon CCR = 0 matches when the counter wraps to 0. ChibiOS's tickless system timer on a 16-bit timer (the
// wideband's TIM4 at 2 kHz) eventually sets its next alarm to exactly 0 at the wrap; in emulation that alarm never
// fired, every timed thread stopped and the F103 sat in its idle loop from 32.768 s of uptime (65536 ticks).
//
// This front forwards every access to the timer and turns a CCRx write of 0 into the auto-reload value, so the match
// comes at the counter's last value, one tick before the wrap. ChibiOS treats an early alarm like any other: it sees
// the timer not yet due and re-arms it.
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Bus;

namespace Antmicro.Renode.Peripherals.Miata
{
    [AllowedTranslations(AllowedTranslation.ByteToDoubleWord | AllowedTranslation.WordToDoubleWord)]
    public class TimerCcrZero : IDoubleWordPeripheral, IKnownSize
    {
        public TimerCcrZero(IMachine machine, IDoubleWordPeripheral timer)
        {
            this.timer = timer;
        }

        public long Size => 0x400;
        public ulong ZeroWrites { get; private set; }

        public uint ReadDoubleWord(long offset)
        {
            return timer.ReadDoubleWord(offset);
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            // CCR1..CCR4 at 0x34, 0x38, 0x3C, 0x40
            if(offset >= 0x34 && offset <= 0x40 && (offset & 3) == 0 && (value & 0xFFFF) == 0)
            {
                if(ZeroWrites++ == 0)
                {
                    this.Log(LogLevel.Info, "CCR write of 0 at 0x{0:X}: matching at the auto-reload value instead", offset);
                }
                value = timer.ReadDoubleWord(0x2C);
            }
            timer.WriteDoubleWord(offset, value);
        }

        public void Reset()
        {
        }

        private readonly IDoubleWordPeripheral timer;
    }
}
