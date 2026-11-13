// Diagnostic for long or stuck runs: every `periodMs` of host (wall) time, logs each machine's virtual time and each
// CPU's PC and halted state ("PROBE ..." at error level), from a host timer thread, so it keeps reporting when the
// emulation stalls and the monitor is busy with a RunFor. Map a PC to a function with arm-none-eabi-addr2line -f.
//   probe: Miata.HostProbe @ sysbus 0xD0002000 { periodMs: 2000 }
using System;
using System.Linq;
using System.Text;
using System.Threading;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.CPU;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class HostProbe : Antmicro.Renode.Peripherals.Bus.IDoubleWordPeripheral, IKnownSize, IDisposable
    {
        public HostProbe(IMachine machine, int periodMs = 2000)
        {
            timer = new Timer(_ => Sample(), null, periodMs, periodMs);
        }

        public long Size => 0x100;

        public uint ReadDoubleWord(long offset) { return 0; }
        public void WriteDoubleWord(long offset, uint value) { }
        public void Reset() { }

        public void Dispose()
        {
            timer.Dispose();
        }

        private void Sample()
        {
            try
            {
                var sb = new StringBuilder("PROBE");
                foreach(var m in EmulationManager.Instance.CurrentEmulation.Machines)
                {
                    var name = EmulationManager.Instance.CurrentEmulation[m];
                    sb.AppendFormat(" {0}: t={1:F6}", name, m.LocalTimeSource.ElapsedVirtualTime.TotalSeconds);
                    foreach(var c in m.SystemBus.GetCPUs().OfType<ICPU>())
                    {
                        sb.AppendFormat(" pc=0x{0:X8}{1} instr={2}", (uint)c.PC.RawValue, c.IsHalted ? " halted" : "",
                            (c as TranslationCPU)?.ExecutedInstructions ?? 0);
                    }
                    sb.Append(';');
                }
                this.Log(LogLevel.Error, sb.ToString());
            }
            catch(Exception e)
            {
                this.Log(LogLevel.Error, "PROBE failed: " + e.Message);
            }
        }

        private readonly Timer timer;
    }
}
