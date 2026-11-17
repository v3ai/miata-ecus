# C077 verdict: partly (mostly already documented)
Checked: AMP MM0105 manual (work/R04-megasquirt-mspnp/txt/amp-pnp-mm0105-installation.txt:131-133) says exactly: MSPNP has no OE immobilizer, dash fault indicator will illuminate and/or flash. Fact true as a competitor statement.
Repo already says so: README.md:101 (no immobiliser), INSTALL.md:256 (car with immobiliser may flash security light; ECU does not talk to it), review brief s6. Not on the website pages (grep of repo/website found nothing).
Not verified: forum claims (jumper, emulation vendor, bulb pulling), and no owner has tested a real car. Applies to 2001-05 boards, ordered and current, but it is a firmware/documentation matter, not a hardware defect; nothing to rework.
Corrected: Repo documents the lamp behaviour in INSTALL.md; remaining gap is product page/pre-purchase notice and untested engine-run behaviour with immobilizer.
Fix: add one line to the product page; test on car.
