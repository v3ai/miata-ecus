// Bus front for a Renode STM32_Timer used as ChibiOS's tickless system timer (the wideband's 16-bit TIM4 at 2 kHz).
// Two gaps in Renode 1.15's STM32_Timer meet at the counter wrap:
//  - a compare value of 0 never matches (the channel is disabled, and re-enabled only while CNT < CCR); on silicon
//    CCR = 0 matches when the counter wraps to 0;
//  - the counter runs 0..ARR-1 (LimitTimer keeps Value % Limit), so with ARR = 0xFFFF it never reads 0xFFFF, and a
//    compare at 0xFFFF falls on the same instant as the wrap, where the timer's own update handler resets the channel
//    and the match can be lost.
// ChibiOS eventually sets its next alarm to exactly 0 or 0xFFFF at the wrap. In emulation that alarm never came (or
// came a full counter period later), every timed thread stopped, and the F103 sat in its idle loop from 32.768 s of
// uptime (65536 ticks).
//
// This front forwards every access to the timer and moves a CCRx write of 0 or of the auto-reload value to 1, so the
// match comes one or two ticks after the wrap. ChibiOS handles a late alarm like any other: the expired timers run and
// the next alarm is set.
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
        public ulong WrapWrites { get; private set; }

        public uint ReadDoubleWord(long offset)
        {
            return timer.ReadDoubleWord(offset);
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            // CCR1..CCR4 at 0x34, 0x38, 0x3C, 0x40
            if(offset >= 0x34 && offset <= 0x40 && (offset & 3) == 0)
            {
                var arr = timer.ReadDoubleWord(0x2C) & 0xFFFF;
                var ccr = value & 0xFFFF;
                if(arr > 1 && (ccr == 0 || ccr == arr))
                {
                    if(WrapWrites++ == 0)
                    {
                        this.Log(LogLevel.Info, "CCR write of 0x{0:X} at 0x{1:X}: matching at 1 instead", ccr, offset);
                    }
                    value = 1;
                }
            }
            timer.WriteDoubleWord(offset, value);
        }

        public void Reset()
        {
        }

        private readonly IDoubleWordPeripheral timer;
    }
}
