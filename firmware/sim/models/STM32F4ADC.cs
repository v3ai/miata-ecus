// STM32F405/407 ADC1/ADC2/ADC3 and the common block (0x40012000, 0x400 bytes) for the miata-ecus firmware-in-the-loop
// simulation. Renode 1.15 ships no STM32F4 ADC, and rusEFI cannot run without one: its battery, ignition-key, sensor
// and knock inputs all come through ChibiOS's ADCv2 driver (software start, scan, DMA, continuous until stopped).
//
// What is modelled:
//  - regular sequence (SQR1-3, L, SCAN), single and continuous mode, software start (SWSTART),
//  - conversion time from SMPRx sample time + 12 ADCCLK cycles, ADCCLK = PCLK2 / ADCPRE (CCR bits 16-17),
//  - 12-bit right/left aligned result in DR, EOC/STRT flags, EOC interrupt, one DMA request per conversion,
//  - per-pin input voltages set from the monitor (SetPinVoltage "PA4" 1.23), VREFINT 1.21 V, temperature sensor.
// Not modelled: injected channels, analog watchdog, overrun (OVR is never set), external triggers, multi-ADC modes,
// resolution other than 12 bit. Unsupported bits are logged once.
using System;
using System.Collections.Generic;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Bus;
using Antmicro.Renode.Peripherals.Timers;
using Antmicro.Renode.Time;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class STM32F4ADC : IDoubleWordPeripheral, IWordPeripheral, IKnownSize
    {
        public STM32F4ADC(IMachine machine, long pclk2Frequency = 84000000, double vdda = 3.3)
        {
            this.machine = machine;
            this.pclk2 = pclk2Frequency;
            this.vdda = vdda;
            IRQ = new GPIO();
            DMA1 = new GPIO();
            DMA2 = new GPIO();
            DMA3 = new GPIO();
            units = new Unit[3];
            for(var i = 0; i < 3; i++)
            {
                units[i] = new Unit(this, i);
            }
            Reset();
        }

        public GPIO IRQ { get; }
        public GPIO DMA1 { get; }
        public GPIO DMA2 { get; }
        public GPIO DMA3 { get; }
        public long Size => 0x400;

        // Voltage on a package pin, e.g. SetPinVoltage "PA4" 1.25
        public void SetPinVoltage(string pin, double volts)
        {
            pinVolts[pin.ToUpperInvariant()] = volts;
        }

        public double GetPinVoltage(string pin)
        {
            return pinVolts.TryGetValue(pin.ToUpperInvariant(), out var v) ? v : 0.0;
        }

        // Peak-to-peak amplitude (V) and frequency (Hz) of a sine added to a pin's DC voltage (knock sensor input).
        public void SetPinSine(string pin, double amplitudeVpp, double frequencyHz)
        {
            sine[pin.ToUpperInvariant()] = new double[] { amplitudeVpp, frequencyHz };
        }

        public ulong Conversions => conversions;

        public void Reset()
        {
            ccr = 0;
            conversions = 0;
            foreach(var u in units)
            {
                u.Reset();
            }
            UpdateIrq();
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
            if(offset >= 0x300)
            {
                switch(offset)
                {
                case 0x300: // CSR: mirror of the three SR registers
                    return (units[0].SR & 0x3F) | ((units[1].SR & 0x3F) << 8) | ((units[2].SR & 0x3F) << 16);
                case 0x304:
                    return ccr;
                case 0x308:
                    return 0;
                }
                return 0;
            }
            return units[offset / 0x100].Read(offset % 0x100);
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            if(offset >= 0x300)
            {
                if(offset == 0x304)
                {
                    ccr = value;
                    if((value & ~0x00C30000u) != 0)
                    {
                        WarnOnce("CCR", value);
                    }
                }
                return;
            }
            units[offset / 0x100].Write(offset % 0x100, value);
        }

        private long AdcClock => pclk2 / (2 * (((ccr >> 16) & 3) + 1));

        private void UpdateIrq()
        {
            var on = false;
            foreach(var u in units)
            {
                on |= u.IrqPending;
            }
            IRQ.Set(on);
        }

        private double PinFor(int adc, int channel, out string name)
        {
            name = null;
            if(channel == 17)
            {
                return 1.21;
            }
            if(channel == 16 || channel == 18)
            {
                return channel == 16 ? 0.76 + 0.0025 * (35 - 25) : 3.0 / 4; // 35 C die, VBAT 3.0 V / 4
            }
            string[] map12 = { "PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PA7", "PB0", "PB1", "PC0", "PC1", "PC2", "PC3", "PC4", "PC5" };
            string[] map3 = { "PA0", "PA1", "PA2", "PA3", "PF6", "PF7", "PF8", "PF9", "PF10", "PF3", "PC0", "PC1", "PC2", "PC3", "PF4", "PF5" };
            name = (adc == 2 ? map3 : map12)[channel & 15];
            var v = GetPinVoltage(name);
            if(sine.TryGetValue(name, out var s) && s[0] > 0)
            {
                var t = machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds;
                v += s[0] / 2 * Math.Sin(2 * Math.PI * s[1] * t);
            }
            return v;
        }

        private void WarnOnce(string what, uint value)
        {
            if(warned.Add(what))
            {
                this.Log(LogLevel.Warning, "{0}: unmodelled bits written (0x{1:X}); only the regular group, software start and 12-bit mode are modelled", what, value);
            }
        }

        private readonly IMachine machine;
        private readonly long pclk2;
        private readonly double vdda;
        private readonly Unit[] units;
        private readonly Dictionary<string, double> pinVolts = new Dictionary<string, double>();
        private readonly Dictionary<string, double[]> sine = new Dictionary<string, double[]>();
        private readonly HashSet<string> warned = new HashSet<string>();
        private uint ccr;
        private ulong conversions;

        private static readonly int[] SampleCycles = { 3, 15, 28, 56, 84, 112, 144, 480 };

        private class Unit
        {
            public Unit(STM32F4ADC parent, int index)
            {
                this.parent = parent;
                this.index = index;
                timer = new LimitTimer(parent.machine.ClockSource, 84000000, parent, "adc" + (index + 1), limit: 1,
                    direction: Direction.Ascending, enabled: false, workMode: WorkMode.OneShot, eventEnabled: true);
                timer.LimitReached += ConversionDone;
            }

            public uint SR;
            public bool IrqPending => ((SR & 2) != 0 && (cr1 & (1 << 5)) != 0);

            public void Reset()
            {
                timer.Enabled = false;
                SR = 0; cr1 = 0; cr2 = 0; smpr1 = 0; smpr2 = 0; sqr1 = 0; sqr2 = 0; sqr3 = 0; dr = 0; htr = 0xFFF; ltr = 0; jsqr = 0;
                position = 0;
                running = false;
            }

            public uint Read(long offset)
            {
                switch(offset)
                {
                case 0x00: return SR;
                case 0x04: return cr1;
                case 0x08: return cr2;
                case 0x0C: return smpr1;
                case 0x10: return smpr2;
                case 0x24: return htr;
                case 0x28: return ltr;
                case 0x2C: return sqr1;
                case 0x30: return sqr2;
                case 0x34: return sqr3;
                case 0x38: return jsqr;
                case 0x4C:
                    SR &= ~2u; // reading DR clears EOC
                    parent.UpdateIrq();
                    return dr;
                }
                return 0;
            }

            public void Write(long offset, uint value)
            {
                switch(offset)
                {
                case 0x00:
                    SR &= value; // rc_w0
                    parent.UpdateIrq();
                    break;
                case 0x04:
                    cr1 = value;
                    // RES (bits 24-25) other than 12 bit, AWD, JEOCIE, DISCEN are not modelled
                    if((value & ~((1u << 5) | (1u << 8) | (1u << 26))) != 0)
                    {
                        parent.WarnOnce("ADC" + (index + 1) + " CR1", value);
                    }
                    break;
                case 0x08:
                    var wasOn = (cr2 & 1) != 0;
                    cr2 = value & ~(1u << 30) & ~(1u << 22);
                    if((value & 1) == 0)
                    {
                        Stop();
                    }
                    if((value & (3u << 28)) != 0)
                    {
                        parent.WarnOnce("ADC" + (index + 1) + " CR2 external trigger", value);
                    }
                    if((value & (1u << 30)) != 0 && wasOn | (value & 1) != 0)
                    {
                        Start();
                    }
                    break;
                case 0x0C: smpr1 = value; break;
                case 0x10: smpr2 = value; break;
                case 0x24: htr = value; break;
                case 0x28: ltr = value; break;
                case 0x2C: sqr1 = value; break;
                case 0x30: sqr2 = value; break;
                case 0x34: sqr3 = value; break;
                case 0x38:
                    jsqr = value;
                    if(value != 0)
                    {
                        parent.WarnOnce("ADC" + (index + 1) + " JSQR", value);
                    }
                    break;
                }
            }

            private int Length => (cr1 & (1 << 8)) != 0 ? (int)((sqr1 >> 20) & 0xF) + 1 : 1;

            private int Channel(int pos)
            {
                if(pos < 6) return (int)((sqr3 >> (5 * pos)) & 0x1F);
                if(pos < 12) return (int)((sqr2 >> (5 * (pos - 6))) & 0x1F);
                return (int)((sqr1 >> (5 * (pos - 12))) & 0x1F);
            }

            private int SampleTime(int ch)
            {
                var smp = ch < 10 ? (smpr2 >> (3 * ch)) & 7 : (smpr1 >> (3 * (ch - 10))) & 7;
                return SampleCycles[smp];
            }

            private void Start()
            {
                position = 0;
                running = true;
                SR |= 1u << 4; // STRT
                Schedule();
            }

            private void Stop()
            {
                running = false;
                timer.Enabled = false;
            }

            private void Schedule()
            {
                var ch = Channel(position);
                timer.Enabled = false;
                timer.Frequency = parent.AdcClock;
                timer.Value = 0;
                timer.Limit = (ulong)(SampleTime(ch) + 12);
                timer.Enabled = true;
            }

            private void ConversionDone()
            {
                if(!running || (cr2 & 1) == 0)
                {
                    return;
                }
                var ch = Channel(position);
                var v = parent.PinFor(index, ch, out var _);
                var code = (int)Math.Round(v / parent.vdda * 4095.0);
                code = Math.Max(0, Math.Min(4095, code));
                dr = (cr2 & (1 << 11)) != 0 ? (uint)(code << 4) : (uint)code;
                SR |= 2; // EOC
                parent.conversions++;
                parent.UpdateIrq();
                if((cr2 & (1 << 8)) != 0)
                {
                    var req = index == 0 ? parent.DMA1 : index == 1 ? parent.DMA2 : parent.DMA3;
                    req.Set(true);
                    req.Set(false);
                }
                position++;
                if(position >= Length)
                {
                    position = 0;
                    if((cr2 & 2) == 0)
                    {
                        running = false;
                        return;
                    }
                }
                if(running && (cr2 & 1) != 0)
                {
                    Schedule();
                }
            }

            private readonly STM32F4ADC parent;
            private readonly int index;
            private readonly LimitTimer timer;
            private uint cr1, cr2, smpr1, smpr2, sqr1, sqr2, sqr3, dr, htr, ltr, jsqr;
            private int position;
            private bool running;
        }
    }
}
