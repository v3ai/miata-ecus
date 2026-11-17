# C025 verification (primary sources)
Verdict: partly (descriptive half true; the "recommended path" half is advice, not checkable fact; not on the ordered hardware).
Checked:
- repo/firmware/README.md:31-37 and repo/README.md:192: customers are told to open an Actions run and download artifacts. No release/tag/checksum text in firmware/README.md (grep).
- repo/.github/workflows/firmware.yaml:4-14: runs on push/PR touching firmware/**; artifacts via actions/upload-artifact@v4 with no retention-days set (grep), so GitHub default applies (90 days, repo-configurable; I did not re-fetch GitHub docs). Downloading artifacts requires a GitHub login (GitHub behaviour, not verified live here).
- Not in review brief section 6 or VERIFICATION.md open items (grep for artifact/release found nothing relevant). Not news-excluded, but low-hardware impact.
- Whether repo has any GitHub Release/tags could not be checked offline.
- Recommendations R13.09 (custom repo, ini hosting at rusEFI, quarterly pin refresh, upstream PR) rest on rusEFI wiki/Strategy docs I did not re-verify; no cost saving claimed.
Corrected statement: Firmware is distributed only as GitHub Actions artifacts of the latest run (default expiry, login needed); no release, tag, checksum or version note is documented. Severity: medium (ux, process), not high.
Fix: publish a GitHub Release per shipped batch with .bin/.dfu/.ini, SHA-256 sums and the pinned rusEFI commit; link it from README/INSTALL and the product page.
Ordered boards: not affected (software distribution only; firmware can be re-released any time).
