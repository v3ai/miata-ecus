# C065 verdict: partly (true as an unknown, overstated as a risk)
Checked: datasheets/txt/C2977586 says "Surface Coating: Au or Over Ni" (plating unspecified or a template line); LCSC Contact Plating is '-'. Both facts are true.
Not verified: the socket C124412 "gold over nickel" claim. Its text datasheet has no plating words, and the repo (VERIFICATION.md:670-674) only asserts "already gold". The claim's "tin or unknown against gold" is speculation; a 0.20 USD header is probably gold-flash or tin.
Repo already documents the tin-vs-gold fretting issue for the hand-fit sockets (VERIFICATION.md:670) but says nothing about the LCSC header C2977586 plating, so the specific gap is not documented.
Affects ordered boards: yes (ord_db BOM contains C2977586 J1/J2). Rework is possible by hand only by swapping the headers; cheaper is to inspect/sample the received header and test contact resistance.
Corrected statement: header plating is undocumented (Au or Ni, not stated); mixed-metal mating with the socket is possible, severity low-medium, unconfirmed. Fix: inspect the delivered parts (magnet/visual/XRF or ask LCSC/Zhouri for a spec); alternatively choose a header with stated gold.
