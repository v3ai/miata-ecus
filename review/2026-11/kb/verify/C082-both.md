# C082 verdict: partly (firmware facts true; stock-ECU behaviour unverified)
Checked:
- repo/firmware/board/miata_board.cpp:92-93,228: fanPin=MIATA_FAN, fan2Pin=MIATA_LS7, only fan1AcMode=Relay set. TRUE.
- rusEFI fan_control.cpp:288-289 defaults both AcMode Disabled; :266 fan2OnTemperature 95; :43 enabledForAc needs AcMode==Relay. TRUE.
- Hellen NB2 board_configuration.cpp:99 sets fan2AcMode=Relay (fan2Pin D9). TRUE. Hellen NB1 (hellenMiataNB1/board_configuration.cpp:84-88) sets fan2Pin but NOT fan2AcMode, so for 1996-2000 the "Hellen" support is pin naming only, not behaviour.
- Net map: ord/cur_mb0105 OUT_FAN=J1.2B, OUT_LS7=J1.2C; ord_mb9900 OUT_FAN=1R, OUT_LS7=1I (pcb_nets.txt). research/pinouts_9605.md labels 1I A/C condenser fan relay, 2C condenser fan relay.
- Not in VERIFICATION.md (grep fan/condens: nothing relevant) nor review brief: not documented.
Not verified: what the stock ECU does (condenser fan with A/C on). No FSM text in repo shows it; the statement itself concedes this.
Also: in 99-00 the radiator fan 1R follows A/C while condenser fan 1I does not; the preset may be backwards for NB1 (condenser fan is the one A/C needs). Real concern is A/C head pressure at idle/standstill with A/C on and CLT < 95 C.
Ordered boards: hardware wiring is identical, so affected only in the sense of the firmware preset; fix is a flash, no rework. Severity medium is reasonable, arguably low (software one-liner).
Fix: set fan2AcMode=Relay (year presets 99-00, 01-05; maybe per car after checking), confirm on car which of 1R/1I/2B/2C the stock ECU turns on with A/C, add to VERIFICATION.md.
