# C095 verdict: refuted as a finding (not applicable)
Claim: forum threads show A/C idle-up stalls on MSPNP; fix = wire A/C request to dedicated input, enable idle-up in base maps, document.
Checked: repo/firmware/board/miata_board.cpp:112 sets acSwitch = MIATA_SW2 (dedicated A/C input, PE10, J2-16); line 219 sets acIdleExtraOffset = 15; line 228 fan1AcMode Relay; A/C relay output on PE6. firmware/README.md:115-118,191 and VERIFICATION.md M4 (line 215) document the A/C input and pull-up. 
The only evidence is a search summary of miataturbo threads about Megasquirt MSPNP, which is a different product; not verified, no primary source. The suggested fix is already done in the repo.
Remaining true part: idle-up delay/duty tuning values are untested on any car (nothing built), and documenting A/C tuning in INSTALL.md could be a minor UX note. Not an ordered-board issue (firmware only, no hardware change).
