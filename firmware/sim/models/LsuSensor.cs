// Bosch LSU 4.9 sensor plant for the wideband controller's firmware-in-the-loop run. It closes the loop the
// firmware runs: heater PWM -> sensor temperature -> Nernst cell resistance (seen through the ESR injection); pump
// current -> Nernst voltage relative to the exhaust lambda. It feeds the F103's ADC inputs just before each
// conversion and reads the firmware's outputs from the F103's own registers:
//   heater duty   TIM2 CCR3 / (ARR + 1)       (PB10, heater driver Q101)
//   pump DAC      TIM3 CCR1 / (ARR + 1)       (PA6, filtered PWM: V = 3.3 V x duty)
//   ESR drive     GPIOB ODR bit 7             (PB7, LSU 4.9 ESR resistor 22k)
// ADC channels, in the scaling the firmware itself uses (firmware/wideband/miata_f1/port.cpp and wideband_config.h):
//   IN0 PA0  Un_sense = 2.7 x (Nernst DC +/- half the ESR swing)
//   IN2 PA2  Ip_sense = Vm - 0.619 V/mA x pump current   (PUMP_CURRENT_SENSE_GAIN 10 x LSU_SENSE_R 61.9)
//   IN3 PA3  Vm = 1.65 V
//   IN8 PB0  battery x 10/110
// The analog front end itself is checked by firmware/tools/circuit_sim_full.py (SPICE); this model uses the
// firmware's own scale factors so that what is tested here is the firmware: heater control, ESR measurement and the
// pump loop. Sensor numbers (LSU 4.9 data sheet, rounded): heater 3.2 ohm cold, about 7.5 W to hold 780 C; Nernst
// cell 300 ohm at 780 C; pump current 0 mA at lambda 1, +2.55 mA in air.
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class LsuSensor : IPeripheral, Antmicro.Renode.Peripherals.Bus.IDoubleWordPeripheral, IKnownSize
    {
        // `adc` is the STM32F1ADC model. Renode compiles each included .cs file on its own, so its type is reached
        // through reflection rather than named here.
        public LsuSensor(IMachine machine, IPeripheral adc)
        {
            this.machine = machine;
            var t = adc.GetType();
            setVoltage = (Action<int, double>)Delegate.CreateDelegate(typeof(Action<int, double>), adc,
                t.GetMethod("SetChannelVoltage"));
            t.GetEvent("BeforeConversion").AddEventHandler(adc, new Action<int>(Update));
            Reset();
        }

        public double Lambda { get; set; } = 1.0;
        public double Battery { get; set; } = 14.0;
        public bool Connected { get; set; } = true;
        public double Temperature { get; private set; }
        public double Esr => Connected ? 300.0 * Math.Exp(-(Temperature - 780.0) / 60.0) : 1e6;
        public double PumpCurrentMa { get; private set; }
        public double NernstVolts { get; private set; }
        public double HeaterWatts { get; private set; }
        public double HeaterDuty { get; private set; }
        public double PumpCommandMa { get; private set; }

        // > 0: log the sensor state every LogEvery virtual seconds ("LSU {json}" at error level, so it shows at logLevel 3)
        public double LogEvery { get; set; }

        public void SetLambda(double lambda) { Lambda = lambda; }
        public void SetBattery(double volts) { Battery = volts; }

        public void Reset()
        {
            Temperature = Ambient;
            lastTime = -1;
        }

        private static double Interp(double x, double[] xs, double[] ys)
        {
            if(x <= xs[0]) return ys[0];
            for(var i = 1; i < xs.Length; i++)
            {
                if(x <= xs[i])
                {
                    return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
                }
            }
            return ys[ys.Length - 1];
        }

        // LSU 4.9 pump current (mA) needed to hold the cavity at lambda 1, by exhaust lambda
        private static readonly double[] LamBins = { 0.65, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.43, 1.70, 2.42, 10.0 };
        private static readonly double[] IpBins = { -2.22, -1.82, -1.11, -0.50, 0.00, 0.33, 0.60, 1.00, 1.32, 1.82, 2.55 };

        private double Duty(ulong timerBase, long ccrOffset)
        {
            var bus = machine.SystemBus;
            var arr = bus.ReadDoubleWord(timerBase + 0x2C);
            var ccr = bus.ReadDoubleWord(timerBase + (ulong)ccrOffset);
            var cr1 = bus.ReadDoubleWord(timerBase);
            if((cr1 & 1) == 0 || arr == 0)
            {
                return 0;
            }
            return Math.Min(1.0, (double)ccr / (arr + 1));
        }

        // Runs before every conversion (about 5 x 10^5 per second); the plant and the firmware's outputs (PWM duties,
        // ESR drive pin) are re-read at most every UpdateStep of virtual time, far shorter than the PWM period (100 us)
        // and the ESR half period (1.2 ms), and the ADC inputs keep their values in between.
        private void Update(int channel)
        {
            var now = machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds;
            if(lastTime >= 0 && now - lastTime < UpdateStep)
            {
                return;
            }
            if(lastTime < 0)
            {
                lastTime = now;
            }
            var dt = now - lastTime;
            lastTime = now;

            // heater: rms power from PWM duty, resistance rising with temperature; lumped thermal mass
            HeaterDuty = Duty(0x40000000, 0x3C);
            var rh = 3.2 * (1 + 0.0028 * (Temperature - 20));
            HeaterWatts = Connected ? HeaterDuty * Battery * Battery / rh : 0;
            if(dt > 0 && dt < 0.1)
            {
                // 7.5 W holds 780 C in 20 C exhaust: loss 0.00987 W/K; 4 s time constant at temperature
                var loss = 0.00987 * (Temperature - Ambient);
                Temperature += dt * (HeaterWatts - loss) / 0.04;
            }

            // pump: command from the DAC, delivered only by a hot cell
            var vdac = 3.3 * Duty(0x40000400, 0x34);
            PumpCommandMa = (1.65 - vdac) / 0.000321162 / 1000.0;
            var hot = Math.Max(0, Math.Min(1, (Temperature - 450) / 250));
            PumpCurrentMa = Connected ? PumpCommandMa * hot : 0;
            var need = Interp(Lambda, LamBins, IpBins);
            // cavity balance: too little pumping in lean exhaust leaves it lean (Nernst below 450 mV), and the
            // reverse for rich; a cold cell gives no voltage
            NernstVolts = Connected ? hot * Math.Max(0.02, Math.Min(0.95, 0.45 + 0.5 * (PumpCurrentMa - need))) : 0;

            var esrHigh = (machine.SystemBus.ReadDoubleWord(0x40010C0C) & (1 << 7)) != 0;
            var total = Esr + 10.0; // Nernst cell + R109 (VM_RESISTOR_VALUE)
            var swing = 3.3 * total / (22000.0 + total);
            var nernstPin = NernstVolts + (esrHigh ? swing / 2 : -swing / 2);

            setVoltage(0, Clamp(2.7 * nernstPin + 2.7 * 0.0));
            setVoltage(2, Clamp(1.65 - 0.619 * PumpCurrentMa));
            setVoltage(3, 1.65);
            setVoltage(8, Clamp(Battery * 10.0 / 110.0));

            if(LogEvery > 0 && now >= nextLog)
            {
                nextLog = now + LogEvery;
                this.Log(LogLevel.Error, string.Format(System.Globalization.CultureInfo.InvariantCulture,
                    "LSU {{\"t\": {0:F4}, \"temp\": {1:F1}, \"esr\": {2:F1}, \"heaterDuty\": {3:F4}, \"heaterW\": {4:F2}, " +
                    "\"ipCmd\": {5:F4}, \"ip\": {6:F4}, \"nernst\": {7:F4}, \"lambda\": {8:F3} }}",
                    now, Temperature, Esr, HeaterDuty, HeaterWatts, PumpCommandMa, PumpCurrentMa, NernstVolts, Lambda));
            }
        }

        private static double Clamp(double v)
        {
            return Math.Max(0, Math.Min(3.3, v));
        }

        private const double Ambient = 20.0;
        private const double UpdateStep = 20e-6;
        private readonly IMachine machine;
        private readonly Action<int, double> setVoltage;
        private double lastTime;
        private double nextLog;

        // Bus presence only (Renode creates a peripheral declared in a platform file only when it is registered or
        // connected); the registers read as 0.
        public long Size => 0x100;
        public uint ReadDoubleWord(long offset) { return 0; }
        public void WriteDoubleWord(long offset, uint value) { }
    }
}
