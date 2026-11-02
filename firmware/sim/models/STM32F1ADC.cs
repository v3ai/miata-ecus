// STM32F103 ADC1 (0x40012400) for the wideband controller's firmware-in-the-loop run. Renode 1.15's F103 platform
// has no ADC. Models what ChibiOS's ADCv1 driver uses: power-up and calibration (ADON, RSTCAL, CAL clear at once),
// start by writing ADON a second time, regular sequence with SCAN, continuous mode, DMA (one request per
// conversion), EOC flag and interrupt, conversion time = sample time + 12.5 ADCCLK, ADCCLK = PCLK2 / ADCPRE read from
// RCC_CFGR. Channel voltages come from the monitor (SetChannelVoltage 0 1.65) or from a connected analog model
// through SetChannelVoltage. Not modelled: injected group, analog watchdog, external triggers, dual mode.
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Bus;
using Antmicro.Renode.Peripherals.Timers;
using Antmicro.Renode.Time;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class STM32F1ADC : IDoubleWordPeripheral, IWordPeripheral, IKnownSize
    {
        public STM32F1ADC(IMachine machine, long pclk2Frequency = 48000000, double vdda = 3.3)
        {
            this.machine = machine;
            this.pclk2 = pclk2Frequency;
            this.vdda = vdda;
            IRQ = new GPIO();
            DMA = new GPIO();
            timer = new LimitTimer(machine.ClockSource, 24000000, this, "adc1", limit: 1, direction: Direction.Ascending,
                enabled: false, workMode: WorkMode.OneShot, eventEnabled: true);
            timer.LimitReached += ConversionDone;
            volts = new double[18];
            volts[16] = 1.43 - 0.0043 * 10; // temperature sensor at ~35 C
            volts[17] = 1.20;               // VREFINT
            Reset();
        }

        public GPIO IRQ { get; }
        public GPIO DMA { get; }
        public long Size => 0x400;
        public ulong Conversions { get; private set; }

        public void SetChannelVoltage(int channel, double v)
        {
            volts[channel] = v;
        }

        public double GetChannelVoltage(int channel)
        {
            return volts[channel];
        }

        // Called with (channel) just before each conversion; an analog model can update the input from it.
        public event Action<int> BeforeConversion;

        public void Reset()
        {
            timer.Enabled = false;
            sr = cr1 = cr2 = smpr1 = smpr2 = sqr1 = sqr2 = sqr3 = dr = 0;
            running = false;
            position = 0;
            IRQ.Unset();
        }

        // DMA reads DR as a half-word (PSIZE = 16 bit)
        public ushort ReadWord(long offset)
        {
            return (ushort)(ReadDoubleWord(offset & ~3L) >> (int)(8 * (offset & 2)));
        }

        public void WriteWord(long offset, ushort value)
        {
            if((offset & 2) == 0)
            {
                WriteDoubleWord(offset, value);
            }
        }

        public uint ReadDoubleWord(long offset)
        {
            switch(offset)
            {
            case 0x00: return sr;
            case 0x04: return cr1;
            case 0x08: return cr2;
            case 0x0C: return smpr1;
            case 0x10: return smpr2;
            case 0x2C: return sqr1;
            case 0x30: return sqr2;
            case 0x34: return sqr3;
            case 0x4C:
                sr &= ~2u;
                UpdateIrq();
                return dr;
            }
            return 0;
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            switch(offset)
            {
            case 0x00:
                sr &= value;
                UpdateIrq();
                break;
            case 0x04:
                cr1 = value;
                if((value & ~((1u << 5) | (1u << 8))) != 0)
                {
                    WarnOnce("CR1", value);
                }
                break;
            case 0x08:
                var wasOn = (cr2 & 1) != 0;
                // CAL (bit 2) and RSTCAL (bit 3) complete at once; SWSTART/JSWSTART are write-only triggers
                cr2 = value & ~((1u << 2) | (1u << 3) | (1u << 21) | (1u << 22));
                if((value & 1) == 0)
                {
                    running = false;
                    timer.Enabled = false;
                    break;
                }
                if((value & (1u << 20)) != 0)
                {
                    WarnOnce("CR2 external trigger", value);
                }
                // F1: setting ADON again (no external trigger) or SWSTART starts the regular group
                if((wasOn && (value & ((1u << 2) | (1u << 3))) == 0) || (value & (1u << 22)) != 0)
                {
                    Start();
                }
                break;
            case 0x0C: smpr1 = value; break;
            case 0x10: smpr2 = value; break;
            case 0x2C: sqr1 = value; break;
            case 0x30: sqr2 = value; break;
            case 0x34: sqr3 = value; break;
            case 0x38:
                if(value != 0)
                {
                    WarnOnce("JSQR", value);
                }
                break;
            }
        }

        private void WarnOnce(string what, uint value)
        {
            if(!warned.Contains(what))
            {
                warned.Add(what);
                this.Log(LogLevel.Warning, "{0}: unmodelled bits written (0x{1:X})", what, value);
            }
        }

        private void UpdateIrq()
        {
            IRQ.Set((sr & 2) != 0 && (cr1 & (1 << 5)) != 0);
        }

        private int Length => (cr1 & (1 << 8)) != 0 ? (int)((sqr1 >> 20) & 0xF) + 1 : 1;

        private int Channel(int pos)
        {
            if(pos < 6) return (int)((sqr3 >> (5 * pos)) & 0x1F);
            if(pos < 12) return (int)((sqr2 >> (5 * (pos - 6))) & 0x1F);
            return (int)((sqr1 >> (5 * (pos - 12))) & 0x1F);
        }

        // sample time in half ADC cycles, including the 12.5-cycle conversion
        private int HalfCycles(int ch)
        {
            var smp = ch < 10 ? (smpr2 >> (3 * ch)) & 7 : (smpr1 >> (3 * (ch - 10))) & 7;
            return SampleHalfCycles[smp] + 25;
        }

        private long AdcClock
        {
            get
            {
                var cfgr = machine.SystemBus.ReadDoubleWord(0x40021004);
                var pre = 2 * (((cfgr >> 14) & 3) + 1);
                return pclk2 / pre;
            }
        }

        private void Start()
        {
            adcClock = AdcClock; // RCC is a Python model: read it once per start, not once per sequence
            running = true;
            position = 0;
            sr |= 1u << 4;
            Schedule();
        }

        // One timer event per regular sequence: it fires when the sequence's last conversion would end and produces
        // the results in order, each with its DMA request (same data and end-of-sequence timing, far fewer events).
        private void Schedule()
        {
            ulong half = 0;
            for(var p = 0; p < Length; p++)
            {
                half += (ulong)HalfCycles(Channel(p));
            }
            timer.Enabled = false;
            var f = 2 * adcClock;
            if(timer.Frequency != f)
            {
                timer.Frequency = f;
            }
            timer.Value = 0;
            timer.Limit = half;
            timer.Enabled = true;
        }

        private void ConversionDone()
        {
            for(var p = 0; p < Length; p++)
            {
                if(!running || (cr2 & 1) == 0)
                {
                    return;
                }
                var ch = Channel(p);
                BeforeConversion?.Invoke(ch);
                var code = (int)Math.Round(volts[ch] / vdda * 4095.0);
                code = Math.Max(0, Math.Min(4095, code));
                dr = (cr2 & (1 << 11)) != 0 ? (uint)(code << 4) : (uint)code;
                sr |= 2;
                Conversions++;
                if((cr2 & (1 << 8)) != 0)
                {
                    DMA.Set(true);
                    DMA.Set(false);
                }
            }
            UpdateIrq();
            if((cr2 & 2) == 0)
            {
                running = false;
                return;
            }
            Schedule();
        }

        private static readonly int[] SampleHalfCycles = { 3, 15, 27, 57, 83, 111, 143, 479 };
        private readonly IMachine machine;
        private readonly long pclk2;
        private readonly double vdda;
        private readonly LimitTimer timer;
        private readonly double[] volts;
        private readonly System.Collections.Generic.HashSet<string> warned = new System.Collections.Generic.HashSet<string>();
        private uint sr, cr1, cr2, smpr1, smpr2, sqr1, sqr2, sqr3, dr;
        private bool running;
        private int position;
        private long adcClock = 12000000;
    }
}
