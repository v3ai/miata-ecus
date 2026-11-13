// Records level changes of MCU output pins with their virtual time, for the firmware-in-the-loop analysis
// (injector pulse widths, ignition dwell and spark angle, relay outputs). Inputs are numbered port * 16 + pin
// (PA0 = 0, PE15 = 79); the platform file wires the pins of interest here in addition to their normal connections.
// Output file lines: "<time ns> <input number> <0|1>".
using System;
using System.IO;
using Antmicro.Renode.Core;
using Antmicro.Renode.Peripherals;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class PinRecorder : IGPIOReceiver
    {
        public PinRecorder(IMachine machine)
        {
            this.machine = machine;
            state = new int[NumberOfInputs];
            for(var i = 0; i < NumberOfInputs; i++)
            {
                state[i] = -1;
            }
        }

        public void SetOutputFile(string path)
        {
            writer?.Dispose();
            writer = new StreamWriter(path, false) { AutoFlush = true };
        }

        public void Flush()
        {
            writer?.Flush();
        }

        public ulong Changes { get; private set; }

        public void OnGPIO(int number, bool value)
        {
            if(number < 0 || number >= NumberOfInputs)
            {
                return;
            }
            var v = value ? 1 : 0;
            if(state[number] == v)
            {
                return;
            }
            state[number] = v;
            Changes++;
            if(writer != null)
            {
                var ns = (long)Math.Round(machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds * 1e9);
                writer.Write(ns);
                writer.Write(' ');
                writer.Write(number);
                writer.Write(' ');
                writer.Write(v);
                writer.Write('\n');
            }
        }

        public void Reset()
        {
            for(var i = 0; i < NumberOfInputs; i++)
            {
                state[i] = -1;
            }
        }

        private const int NumberOfInputs = 144;
        private readonly IMachine machine;
        private readonly int[] state;
        private StreamWriter writer;
    }
}
