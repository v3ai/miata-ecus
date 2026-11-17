# C129 verification: ZXMS open-drain ignition option
Verdict: PARTLY (saving arithmetic true; electrical function unverifiable without igniter input data).
Checked:
- design.py:297-335: U6/U7 TC4427, U13 74HCT04, R15-18 (100R 1206), R144-147 (3.3k 1206), C34/C35 as claimed. Current rev 0.10 only.
- Prices (kb/parts_manifest.json): TC4427 C20551 qty100 $0.4762 (2 = $0.95); 74HCT04 C131317 ~ $0.15 (earlier claim); resistors ~$0.003. Gross ~ $1.1-1.2; the 4 new 1k 1206 pull-ups cost ~$0.02, so net ~ $1.1. OK.
- ZXMS6004FF datasheet: VIH min 3 V, VIN max 6 V abs / 5.5 V recommended, input current 120 uA at 5 V. A 10k pull-up to 5V gives gate 5V in reset (on, output low): fine. 3 V is the min VIH, so a push-pull 3.3 V MCU high has little margin; better to make the MCU pin open-drain (rusEFI supports OM_OPENDRAIN, already used for driverEnable in board_configuration.cpp:110) so the gate reaches 5 V.
- IGN CTL pins are U1.95-98 = PB8, PB9, PE0, PE1: these are 5V-tolerant (FT) pins on STM32F407, so 5 V pull-up is allowed when VDD is present. VDD=0 case not checked (the claim itself says not read).
- Not documented in VERIFICATION.md or review brief as an open item. Rev 0.9 ordered boards: not affected (rev 0.10 only), cannot be changed.
Caveats: high level becomes 5V - Schottky drop (~0.3-0.4 V) divided by 1k against igniter input R (and the existing 3.3k pull-down, which would need removal); igniter input data not in repo. Rise edge (dwell start) slower, spark edge is the ZXMS turn-on, which is already the case today. Side benefit not mentioned: removes the TC4427 4.5 V undervoltage concern (VERIFICATION N13).
Corrected statement: Option is plausible and saves ~$1.1/board at qty100 (+2 extended parts: TC4427, 74HCT04); use open-drain MCU outputs with 10k to +5V and 1k+Schottky pull-up, drop R144-147; adopt only after measuring igniter input resistance/threshold.
