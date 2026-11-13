// Crank/cam signal generator for the firmware-in-the-loop simulation: drives up to four GPIO lines (Ch0..Ch3, wired
// to the MCU's hall inputs in the platform file) with edges placed exactly in virtual time.
//
// Two sources of edges:
//  - a recorded capture, replayed at its own timing:  LoadCapture @file.csv  (lines "time_s,channel,level")
//  - one engine cycle given in crank degrees, looped at a set speed:  LoadPattern @file.csv 720  (lines
//    "angle_deg,channel,level"), then SetRpm 3000. RPM changes take effect from the next edge.
// Start begins playback from now; a capture ends after its last edge, a pattern runs until Stop.
// The generator logs nothing per edge; EdgeCount and CyclesCompleted can be read from the monitor, and
// CycleStartTime (virtual seconds of the most recent pattern angle 0) lets an analysis script turn output timestamps
// into engine angles.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Timers;
using Antmicro.Renode.Time;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class TriggerWheel : IPeripheral
    {
        public TriggerWheel(IMachine machine)
        {
            this.machine = machine;
            Ch0 = new GPIO(); Ch1 = new GPIO(); Ch2 = new GPIO(); Ch3 = new GPIO();
            outputs = new[] { Ch0, Ch1, Ch2, Ch3 };
            timer = new LimitTimer(machine.ClockSource, TickHz, this, "wheel", limit: 1, direction: Direction.Ascending,
                enabled: false, workMode: WorkMode.OneShot, eventEnabled: true);
            timer.LimitReached += OnEdge;
        }

        public GPIO Ch0 { get; }
        public GPIO Ch1 { get; }
        public GPIO Ch2 { get; }
        public GPIO Ch3 { get; }

        public void LoadCapture(string path)
        {
            edges = Parse(path);
            edges.Sort((a, b) => a.Position.CompareTo(b.Position));
            pattern = false;
        }

        public void LoadPattern(string path, double cycleDegrees)
        {
            edges = Parse(path);
            for(var i = 0; i < edges.Count; i++)
            {
                edges[i] = new Edge { Position = ((edges[i].Position % cycleDegrees) + cycleDegrees) % cycleDegrees, Channel = edges[i].Channel, Level = edges[i].Level };
            }
            edges.Sort((a, b) => a.Position.CompareTo(b.Position));
            cycle = cycleDegrees;
            pattern = true;
        }

        public void SetRpm(double rpm)
        {
            Rpm = rpm;
        }

        // Set every output to a level without an edge schedule (e.g. "sensor unplugged": SetLevel 0 true).
        public void SetLevel(int channel, bool level)
        {
            outputs[channel].Set(level);
        }

        public double Rpm { get; private set; }
        public ulong EdgeCount { get; private set; }
        public ulong CyclesCompleted { get; private set; }
        public double CycleStartTime { get; private set; }
        public bool Running { get; private set; }

        public void Start()
        {
            if(edges == null || edges.Count == 0)
            {
                this.Log(LogLevel.Error, "no edges loaded");
                return;
            }
            index = 0;
            Running = true;
            startTime = Now;
            CycleStartTime = startTime;
            ScheduleNext(pattern ? edges[0].Position : edges[0].Position);
        }

        public void Stop()
        {
            Running = false;
            timer.Enabled = false;
        }

        public void Reset()
        {
            Stop();
            foreach(var o in outputs)
            {
                o.Unset();
            }
            EdgeCount = 0;
            CyclesCompleted = 0;
        }

        private double Now => machine.LocalTimeSource.ElapsedVirtualTime.TotalSeconds;

        // delta: seconds (capture) or degrees (pattern) from the current position to the next edge
        private void ScheduleNext(double delta)
        {
            double seconds;
            if(pattern)
            {
                if(Rpm <= 0)
                {
                    Running = false;
                    return;
                }
                seconds = delta / (6.0 * Rpm);
            }
            else
            {
                seconds = delta;
            }
            var ticks = (ulong)Math.Max(1, Math.Round(seconds * TickHz));
            timer.Enabled = false;
            timer.Value = 0;
            timer.Limit = ticks;
            timer.Enabled = true;
        }

        private void OnEdge()
        {
            if(!Running)
            {
                return;
            }
            var e = edges[index];
            outputs[e.Channel].Set(e.Level);
            EdgeCount++;
            var here = e.Position;
            index++;
            if(index >= edges.Count)
            {
                if(!pattern)
                {
                    Running = false;
                    return;
                }
                index = 0;
                CyclesCompleted++;
                var toWrap = cycle - here;
                // angle 0 of the next cycle is reached toWrap degrees from now
                CycleStartTime = Now + (Rpm > 0 ? toWrap / (6.0 * Rpm) : 0);
                ScheduleNext(toWrap + edges[0].Position);
                return;
            }
            ScheduleNext(edges[index].Position - here);
        }

        private static List<Edge> Parse(string path)
        {
            var list = new List<Edge>();
            foreach(var raw in File.ReadAllLines(path))
            {
                var line = raw.Trim();
                if(line.Length == 0 || line[0] == '#' || char.IsLetter(line[0]))
                {
                    continue;
                }
                var f = line.Split(',');
                list.Add(new Edge
                {
                    Position = double.Parse(f[0].Trim(), CultureInfo.InvariantCulture),
                    Channel = int.Parse(f[1].Trim(), CultureInfo.InvariantCulture),
                    Level = f[2].Trim() == "1"
                });
            }
            return list;
        }

        private struct Edge
        {
            public double Position;
            public int Channel;
            public bool Level;
        }

        private const long TickHz = 10000000;
        private readonly IMachine machine;
        private readonly GPIO[] outputs;
        private readonly LimitTimer timer;
        private List<Edge> edges;
        private bool pattern;
        private double cycle = 720;
        private int index;
        private double startTime;
    }
}
