// STM32F103 flash program/erase controller (FPEC, 0x40022000) for the wideband's settings storage (MFS on pages
// 56-63) and for anything that erases flash. Renode 1.15 has no F1 flash controller: writes to the flash memory
// itself always land, but without this model an erase never happens and the firmware's status polling sees garbage.
// Models KEYR unlock/LOCK, page erase (PER + AR + STRT), mass erase (MER + STRT), the PG bit, BSY/EOP/PGERR/WRPRTERR
// flags, and a flash program attempt while locked or without PG is logged (real silicon would raise PGERR and keep
// the old content; the emulated memory has already taken the write). Erase sets the bytes to 0xFF immediately.
using System;
using Antmicro.Renode.Core;
using Antmicro.Renode.Logging;
using Antmicro.Renode.Peripherals.Bus;

namespace Antmicro.Renode.Peripherals.Miata
{
    public class STM32F1Flash : IDoubleWordPeripheral, IKnownSize
    {
        public STM32F1Flash(IMachine machine, ulong flashBase = 0x08000000, uint flashSize = 0x10000, uint pageSize = 0x400)
        {
            this.machine = machine;
            this.flashBase = flashBase;
            this.flashSize = flashSize;
            this.pageSize = pageSize;
            Reset();
        }

        public long Size => 0x400;
        public ulong PageErases { get; private set; }
        public ulong MassErases { get; private set; }

        public void Reset()
        {
            acr = 0x30;
            cr = 0x80; // LOCK
            sr = 0;
            ar = 0;
            keyStep = 0;
        }

        public uint ReadDoubleWord(long offset)
        {
            switch(offset)
            {
            case 0x00: return acr;
            case 0x0C: return sr;
            case 0x10: return cr;
            case 0x14: return ar;
            case 0x1C: return 0x03FFFFFC; // OBR: no read protection, default user bytes
            case 0x20: return 0xFFFFFFFF; // WRPR: nothing write protected
            }
            return 0;
        }

        public void WriteDoubleWord(long offset, uint value)
        {
            switch(offset)
            {
            case 0x00:
                acr = value;
                break;
            case 0x04: // KEYR
                if(keyStep == 0 && value == 0x45670123)
                {
                    keyStep = 1;
                }
                else if(keyStep == 1 && value == 0xCDEF89AB)
                {
                    cr &= ~0x80u;
                    keyStep = 0;
                }
                else
                {
                    this.Log(LogLevel.Warning, "bad flash key sequence (0x{0:X}): locked until reset", value);
                    keyStep = 2;
                }
                break;
            case 0x0C: // SR: EOP, WRPRTERR, PGERR are write-1-to-clear
                sr &= ~(value & 0x34);
                break;
            case 0x10:
                if((cr & 0x80) != 0)
                {
                    this.Log(LogLevel.Warning, "write to FLASH_CR while locked (0x{0:X}) ignored", value);
                    break;
                }
                cr = value & 0x16F7;
                if((value & 0x40) != 0) // STRT
                {
                    if((value & 0x2) != 0)
                    {
                        ErasePage(ar);
                    }
                    else if((value & 0x4) != 0)
                    {
                        Fill(flashBase, flashSize);
                        MassErases++;
                    }
                    cr &= ~0x40u;
                    sr |= 0x20; // EOP
                }
                break;
            case 0x14:
                ar = value;
                break;
            }
        }

        private void ErasePage(uint address)
        {
            var start = (address - (uint)flashBase) / pageSize * pageSize;
            if(start >= flashSize)
            {
                this.Log(LogLevel.Warning, "page erase outside flash (0x{0:X})", address);
                return;
            }
            Fill(flashBase + start, pageSize);
            PageErases++;
        }

        private void Fill(ulong start, uint size)
        {
            for(ulong a = 0; a < size; a += 4)
            {
                machine.SystemBus.WriteDoubleWord(start + a, 0xFFFFFFFF);
            }
        }

        private readonly IMachine machine;
        private readonly ulong flashBase;
        private readonly uint flashSize;
        private readonly uint pageSize;
        private uint acr, cr, sr, ar;
        private int keyStep;
    }
}
