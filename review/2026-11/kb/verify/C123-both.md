# C123 verdict: partly (low-medium, not ordered-board specific)
Checked: onefastshop page fetched live 2026-11-16: contains "Sold out" and "Week of Nov 30" (supports the out-of-stock/ship-date claim; page also has an `"available":true` flag, probably another variant, so stock is ambiguous). iagperformance not rechecked. Price range 22-51 USD is from the audit's notes, not rechecked.
Repo: INSTALL.md section 6 item 3 already says the harness is unchecked and names it as the lead; README says the harness is "never tried on a board". No second lead option is offered in INSTALL.md. R15 notes (kb/R15 area) already recommend a seller-made JST pigtail.
Stated consequence (single source, fragile dependency) is a reasonable inference. A 2-3 week stock gap at one retailer is a transient observation, not a supply problem. The more serious issue is the unverified connector fit, which is already documented.
Ordered boards: no (a documentation/procurement matter, not a board fault).
Fix: INSTALL.md should name a fallback (seller-made pigtail or a Bosch LSU plug with crimped leads). Severity low.
