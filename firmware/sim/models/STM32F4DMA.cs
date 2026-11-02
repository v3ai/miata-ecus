// STM32F4 DMA controller (stream DMA, RM0090 section 10), used for DMA2 in the ECU simulation. Renode 1.15's
// STM32DMA has no circular mode, no half-transfer flag, NDTR that never counts down and an end-of-transfer interrupt
// that is delayed to the next synchronisation point; ChibiOS's ADC driver relies on all of these, and with them
// missing the ADCs free-run between the end of a block and the late interrupt (slow, and wrong data timing).
// Modelled: 8 streams, LISR/HISR/LIFCR/HIFCR, SxCR/NDTR/PAR/M0AR/M1AR/FCR; peripheral requests on GPIO inputs
// 0-7 (one data item per request for peripheral-to-memory), memory-to-peripheral and memory-to-memory transfers done
// at enable, PINC/MINC, PSIZE/MSIZE, circular mode, double-buffer mode (CT swaps at each block end), HT/TC flags and
// interrupts raised at once. Not modelled: FIFO thresholds and bursts (direct mode behaviour), priorities, errors.
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Bus;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class STM32F4DMA : IDoubleWordPeripheral, IKnownSize, IGPIOReceiver, INumberedGPIOOutput
    {
        public STM32F4DMA(IMachine machine)
        {
            this.machine = machine;
            var c = new System.Collections.Generic.Dictionary<int, IGPIO>();
            for(var i = 0; i < 8; i++)
            {
                streams[i] = new Stream();
                c[i] = new GPIO();
            }
            Connections = c;
            Reset();
        }

        public System.Collections.Generic.IReadOnlyDictionary<int, IGPIO> Connections { get; }
        public long Size => 0x400;
        public ulong Transfers { get; private set; }
        public ulong IgnoredRequests { get; private set; }

        public void Reset()
        {
            foreach(var s in streams)
            {
                s.Cr = 0; s.Ndtr = 0; s.Par = 0; s.M0ar = 0; s.M1ar = 0; s.Fcr = 0x21; s.Flags = 0; s.Index = 0;
            }
            Update();
        }

        public uint ReadDoubleWord(long offset)
        {
            if(offset == 0x00 || offset == 0x04)
            {
                var b = offset == 0x00 ? 0 : 4;
                uint v = 0;
                for(var i = 0; i < 4; i++)
                {
                    v |= (uint)streams[b + i].Flags << FlagShift[i];
                }
                return v;
            }
            if(offset < 0x10)
            {
                return 0;
            }
            var n = (int)((offset - 0x10) / 0x18);
            if(n > 7)
            {
                return 0;
            }
            var s = streams[n];
            switch((offset - 0x10) % 0x18)
            {
            case 0x00: return s.Cr;
            case 0x04: return s.Ndtr;
            case 0x08: return s.Par;
            case 0x0C: return s.M0ar;
            case 0x10: return s.M1ar;
            case 0x14: return s.Fcr;
            }
            return 0;
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            if(offset == 0x08 || offset == 0x0C)
            {
                var b = offset == 0x08 ? 0 : 4;
                for(var i = 0; i < 4; i++)
                {
                    streams[b + i].Flags &= (byte)~((value >> FlagShift[i]) & 0x3D);
                }
                Update();
                return;
            }
            if(offset < 0x10)
            {
                return;
            }
            var n = (int)((offset - 0x10) / 0x18);
            if(n > 7)
            {
                return;
            }
            var s = streams[n];
            var enabled = (s.Cr & 1) != 0;
            switch((offset - 0x10) % 0x18)
            {
            case 0x00:
                if(enabled && (value & 1) != 0)
                {
                    // only EN can be changed while enabled (and CT in double-buffer mode); keep the rest
                    s.Cr = (s.Cr & ~(1u << 19)) | (value & (1u << 19));
                    break;
                }
                s.Cr = value;
                if(!enabled && (value & 1) != 0)
                {
                    s.Index = 0;
                    s.Initial = s.Ndtr;
                    var dir = (value >> 6) & 3;
                    if(dir != 0)
                    {
                        // memory-to-peripheral and memory-to-memory: the whole block at once
                        while((s.Cr & 1) != 0 && s.Ndtr > 0)
                        {
                            Item(n, s, dir);
                        }
                    }
                }
                break;
            case 0x04:
                if(!enabled) { s.Ndtr = value & 0xFFFF; }
                break;
            case 0x08:
                if(!enabled) { s.Par = value; }
                break;
            case 0x0C:
                s.M0ar = value;
                break;
            case 0x10:
                s.M1ar = value;
                break;
            case 0x14:
                s.Fcr = (s.Fcr & 0x38) | (value & 0x87);
                break;
            }
            Update();
        }

        public void OnGPIO(int number, bool value)
        {
            if(!value || number < 0 || number > 7)
            {
                return;
            }
            var s = streams[number];
            if((s.Cr & 1) == 0 || s.Ndtr == 0 || ((s.Cr >> 6) & 3) != 0)
            {
                IgnoredRequests++;
                return;
            }
            Item(number, s, 0);
            Update();
        }

        private static int SizeOf(uint code) { return code == 0 ? 1 : code == 1 ? 2 : 4; }

        private void Item(int n, Stream s, uint dir)
        {
            var psize = SizeOf((s.Cr >> 11) & 3);
            var msize = SizeOf((s.Cr >> 13) & 3);
            var pinc = (s.Cr & (1 << 9)) != 0;
            var minc = (s.Cr & (1 << 10)) != 0;
            var dbm = (s.Cr & (1 << 18)) != 0;
            var mem = dbm && (s.Cr & (1 << 19)) != 0 ? s.M1ar : s.M0ar;
            ulong src, dst;
            int rs, ws;
            if(dir == 0)
            {
                src = s.Par + (ulong)(pinc ? s.Index * psize : 0);
                dst = mem + (ulong)(minc ? s.Index * msize : 0);
                rs = psize; ws = msize;
            }
            else
            {
                // M2P and M2M: PAR is the destination for M2P, the source for M2M (RM0090)
                if(dir == 1)
                {
                    src = mem + (ulong)(minc ? s.Index * msize : 0);
                    dst = s.Par + (ulong)(pinc ? s.Index * psize : 0);
                    rs = msize; ws = psize;
                }
                else
                {
                    src = s.Par + (ulong)(pinc ? s.Index * psize : 0);
                    dst = mem + (ulong)(minc ? s.Index * msize : 0);
                    rs = psize; ws = msize;
                }
            }
            var bus = machine.SystemBus;
            ulong v = rs == 1 ? bus.ReadByte(src) : rs == 2 ? bus.ReadWord(src) : bus.ReadDoubleWord(src);
            if(!FastRamWrite(dst, ws, (uint)v))
            {
                if(ws == 1) bus.WriteByte(dst, (byte)v);
                else if(ws == 2) bus.WriteWord(dst, (ushort)v);
                else bus.WriteDoubleWord(dst, (uint)v);
            }
            Transfers++;
            s.Index++;
            s.Ndtr--;
            if(s.Ndtr == s.Initial / 2)
            {
                s.Flags |= 1 << 4; // HTIF
            }
            if(s.Ndtr == 0)
            {
                s.Flags |= 1 << 5; // TCIF
                if((s.Cr & (1 << 8)) != 0 || dbm)
                {
                    s.Ndtr = s.Initial;
                    s.Index = 0;
                    if(dbm)
                    {
                        s.Cr ^= 1u << 19;
                    }
                }
                else
                {
                    s.Cr &= ~1u;
                }
            }
        }

        // Writes into RAM straight into the memory's backing store. Going through the system bus makes Renode check
        // every write for translated code to invalidate (a dynamic call per write), which at the ADC's few hundred
        // thousand transfers a second dominated the emulation time. DMA targets data buffers, never code.
        private bool FastRamWrite(ulong address, int size, uint value)
        {
            if(ramMemory == null || address < ramStart || address + (ulong)size > ramEnd)
            {
                var reg = machine.SystemBus.WhatIsAt(address);
                var mem = reg?.Peripheral as Antmicro.Renode.Peripherals.Memory.MappedMemory;
                if(mem == null)
                {
                    return false;
                }
                ramMemory = mem;
                ramStart = reg.RegistrationPoint.Range.StartAddress;
                ramEnd = reg.RegistrationPoint.Range.EndAddress + 1;
            }
            var offset = (long)(address - ramStart);
            var segment = (int)(offset / ramMemory.SegmentSize);
            var local = offset % ramMemory.SegmentSize;
            if(local + size > ramMemory.SegmentSize)
            {
                return false;
            }
            ramMemory.TouchSegment(segment);
            var p = new IntPtr(ramMemory.GetSegment(segment).ToInt64() + local);
            if(size == 1) System.Runtime.InteropServices.Marshal.WriteByte(p, (byte)value);
            else if(size == 2) System.Runtime.InteropServices.Marshal.WriteInt16(p, unchecked((short)value));
            else System.Runtime.InteropServices.Marshal.WriteInt32(p, unchecked((int)value));
            return true;
        }

        private Antmicro.Renode.Peripherals.Memory.MappedMemory ramMemory;
        private ulong ramStart, ramEnd;

        private void Update()
        {
            for(var i = 0; i < 8; i++)
            {
                var s = streams[i];
                var irq = ((s.Flags & (1 << 5)) != 0 && (s.Cr & (1 << 4)) != 0)
                    || ((s.Flags & (1 << 4)) != 0 && (s.Cr & (1 << 3)) != 0);
                Connections[i].Set(irq);
            }
        }

        private class Stream
        {
            public uint Cr, Ndtr, Par, M0ar, M1ar, Fcr, Initial;
            public int Index;
            public byte Flags;
        }

        private static readonly int[] FlagShift = { 0, 6, 16, 22 };
        private readonly IMachine machine;
        private readonly Stream[] streams = new Stream[8];
    }
}
