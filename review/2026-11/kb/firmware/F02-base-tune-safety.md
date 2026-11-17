# F02 - Base tune and protective defaults

Status: COMPLETE in this pass (see Not checked). Scratch: work/F02-base-tune-safety/ (interp.h = libfirmware interpolation.h fetched from GitHub master).

## Summary
1. Stock engine, first start: mostly safe-to-marginal. Tables are rusEFI's from running cars (NA 1.6 2020, NB 2017); nothing here was run on this board. Hard limit 7200 rpm fuel+spark cut is on; closed-loop trim is bounded +-10 % (+10/-5 in power region).
2. Boosted engine on base tune: UNSAFE. No boost cut, no lambda protection, no overheat cut, no oil protection by default (all verified off). Fuel above the last table row is flat (clamped); NB VE is a flat 80 from 116 kPa (hand-filled, not tuned); NA ignition retains 18-22 deg at 160 kPa. README admits "needs a tuner" but ships protections off.
3. Failed MAP sensor falls back to a 60 kPa flat estimate table (no TPS dependence in the shipped table): at WOT the engine is fuelled for 60 kPa. With boost cut disabled and STFT unable to correct that, a MAP wiring fault = lean WOT.
4. NA 1989-95 presets: idle PID output is pinned to +20 % (minValue 20, maxValue default 20) on top of a generic 75->50 % open-loop IAC curve, so "closed-loop idle" is not closed loop. The tuned 20-28 % idle curve upstream left as a todo comment.
5. Dwell is a constant 4 ms with no voltage correction (default 1.0 across 8-15 V): marginal at cranking/low battery, no coil saturation data found for NA igniter or NB coil pack (UNVERIFIED).
6. Failure fallbacks that are fine: failed CLT turns the fan on; failed wideband = no STFT; failed CLT cranking at 20 C.
7. Ordered boards: same firmware logic; all findings are firmware settings, fixable by reflashing (no rework).

## Evidence tables (VERIFIED unless noted)
Interpolation: libfirmware getBin (interp.h lines 24-60): value >= last bin returns {N-2, frac 1.0} = last cell value; below first bin = first cell. Pinned libfirmware submodule empty in checkout, so master was read (pinned version UNVERIFIED but this behaviour is long-standing).

| Item | 1989-93 NA6 | 1994-95 NA94 | 1996-97 NA96 | 1999-2000 NB1 | 2001-05 NB2 |
|---|---|---|---|---|---|
| displacement L | 1.6 | 1.8 | 1.839 | 1.839 | 1.839 |
| injector cc/min | 212 | 254 | 265 | 256 | 265 |
| injection | batch | sequential | sequential | sequential | sequential |
| VE table | 1.6 table, load 20-128 kPa, rpm 650-7800 | same | same | NB table load 20-220, rpm 700-8000 | same |
| VE at 99 kPa (approx) | 104-125 | same | same | 75-78 | same |
| VE above last row | flat at 128 kPa row (104-130) | same | same | 80 flat from 116 kPa | same |
| dead time | rusEFI default Bosch 0280155868 table (default_fuel.cpp:8) | same | same | NB table 4.0 ms @6V ... 1.2 ms @15V, 12 V 1.5 ms (miata_nb_tune.cpp) | same |
| fuel pressure assumption | fuelReferencePressure 300 kPa default, compensation mode default (not set) | same | same | same | 400 kPa, ICM_FixedRailPressure |
| MAP type | MPX4250 sensor type then overridden by board custom 0-700 kPa | idem | idem | idem | idem |
| ignition table | NA table (mazda_miata_base_maps.cpp) load 10-250 kPa | same | same | NB table load 25-250 | same |
| cranking timing | 10 | 10 | 6 | default 6 (DEFAULT_CRANKING_ANGLE) | same |
| cranking dwell | 6 ms (default) | 6 | 4 | 4 | 4 |
| cranking base fuel | 27.5 mg | 27.5 | 27.5 | 27.5 | 27.5 |
| idle mode | IM_AUTO, PID min20/max20 (pinned) | same | IM_AUTO min-20/max20 | min -8/max 10 | same |
| rev limit | 7200, fuel+spark cut, hyst 50 | | | | |
| fans C (on/off) | 92/88 default | 100/96, fan2 95/91 | 92/88 | 92/88 | 92/88 |

NA ignition (deg BTDC) by load, selected rpm (500,800,1000,1500,1800,2300,2900,3400,3900,4300,4800,5300,5900,6500,7200,8000):
- 10 kPa: 15 15 20 21 32 33 34 35 37 37 38 38 38 39 40 41
- 99 kPa: 19 19 23 26 26 26 26 26 26 27 29 29 30 31 32 32
- 125 kPa: 17 18 21 25 26 27 26 25 24 25 25 26 26 27 28 29
- 160 kPa (8.7 psi): 13 15 18 22 22 22 21 19 18 18 18 18 19 20 20 21
NB ignition (rpm 700..8000): 135 kPa: 13 13 14 14 15 15 17 17 19 20 22 23 24 25 26 27; 158 kPa: 11 11 11 12 12 13 14 15 16 17 19 20 21 22 24 25.
Target lambda (rusEFI default, all years): 1.0 up to 60 kPa, 0.95 @80, 0.90 @100, 0.84 @150, 0.80 @175, 0.73 @250.

## Ratings (stock engine / boosted engine)
| Item | Stock | Boosted | Reason |
|---|---|---|---|
| VE table shape | marginal | unsafe | NA table VE values >100 % (up to 130): physically implausible, absorbs injector/dead-time errors of its source car, applied to 1.8 cars with other injectors (INFERRED). NB flat 80 above 116 kPa is invented. Wideband trim +10 % max in power. |
| Fuel above table | safe (NA 128 kPa row is above atmosphere) | unsafe | clamped flat; speed-density scales with MAP so fuel rises, but VE is not measured |
| Ignition NA at 99 kPa 26 deg | marginal | n/a | Miata 91 oct references found only as forum rules of thumb; UNVERIFIED |
| Ignition NA/NB boost rows | n/a | unsafe | NA 18-22 deg at 160 kPa, NB 24-25 at 6800 rpm 158 kPa; rule of thumb ~1 deg/psi pull from NA (UNVERIFIED, forum) gives ~12-16 at 8 psi, and these are also coupled to unverified fuel |
| Target lambda | safe | marginal | 0.80 @175 kPa is fine IF delivered; delivery unverified |
| Cranking | safe/marginal | same | 27.5 mg cycle base, CLT multiplier 2.8x at -20 C; cold start unproven on this injector set |
| Warm-up / ASE | safe | safe | default 1.5 @-40 -> 1.0 @80 C; ASE 1.2 decaying 150 revs |
| Accel enrichment | safe | marginal | TPS AE defaults + wall wetting 0.3/0.3 (non-test) generic |
| Decel fuel cut | safe (off by default) | safe | coastingFuelCutEnabled = false |
| Idle NA6/NA94 | marginal | n/a | PID pinned, open loop 50-75 % base +20 %: possible high idle/surging; INFERRED |
| Idle NB | marginal | n/a | open-loop curve is generic 75 -> 50 % (default_engine, engine_configuration.cpp:365) since miataNA_setCltIdleCorr only sets bins (todo values commented) |
| Rev limit 7200 fuel+spark | safe | safe | spark cut at limit risks backfire; stock is ~6500-7000 UNVERIFIED |
| Closed-loop fuel +-10 % | safe | marginal | sensor must be right; power region +10/-5 (miata_board.cpp:150) sensible |
| Fan 92/88 | safe | marginal | no CLT overheat cut |
| Dwell 4 ms const | marginal | marginal | no voltage correction; stock coils needs unknown |
| Trigger offset 0 | marginal | unsafe | NA CAS is rotatable, offset off by N deg = timing off by N deg until a timing light check; NB fixed. README step 11 covers; boosted cars gain nothing from it |
| MAP sampling | safe | safe | isMapAveragingEnabled true, board standard |
| MAP failed | unsafe | unsafe | fallback table flat 60 kPa |
| CLT failed | safe | safe | fan on, 20 C cranking |
| IAT failed | safe | safe | corr = 1 |
| Wideband failed | safe | marginal | no trim; fuel stays open loop on base tune |
| Boost cut | n/a | unsafe | boostCutPressure 0 (off) |
| Lambda protection | n/a | unsafe | lambdaProtectionEnable false |
| Overheat cut / CLT rev limit | marginal | marginal | useCltBasedRpmLimit off |
| Oil pressure | n/a | n/a | no sensor on board; off |
| Launch / nitrous | safe (off) | safe | flex/nitrous not assigned |
| Injector staging | none | n/a | by design |

## Sources actually read
repo/firmware/README.md 88-112, 244-252; board/miata_board.cpp (all), board_configuration.cpp, miata_nb_tune.cpp; ext/rusefi firmware/config/engines/mazda/{mazda_miata_1_6.cpp, mazda_miata_na8.cpp, mazda_miata_vvt.cpp (grep), mazda_miata_base_maps.cpp}; controllers/algo/defaults/*.cpp; controllers/algo/engine_configuration.cpp:365,505-560; controllers/limp_manager.cpp; controllers/math/closed_loop_fuel.cpp; controllers/actuators/idle_thread.cpp:330-500; util/math/efi_pid.cpp; modules/fan_control; algo/fuel_math.cpp; algo/airmass/speed_density_airmass.cpp; github rusefi/libfirmware interpolation.h. Web searches for coil dwell and boost timing returned only forum anecdotes.

## Not checked
- FOME equivalents not fetched. Pinned libfirmware not available (master used).
- Dwell: no authoritative NA igniter / NB coil dwell found. Stock injector dead times, real fuel pressures of each year.
- Actual idle behaviour of valve at 70 % duty; units of idle open-loop curve.
- NA/NB trigger decoder tdc offsets (trigger_mazda.cpp not read).
- Mapping of defaults for fanOn on NA6 preset (92/88 default by inference of fan_control.cpp:264 call site).
