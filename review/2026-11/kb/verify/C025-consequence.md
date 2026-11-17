# C025 consequence check
Verdict: partly (low-medium, not high).
Checked: repo/firmware/README.md "Getting the firmware" tells users to open an Actions run and download artifacts; .github/workflows/firmware.yaml triggers on push/PR/dispatch touching firmware/, uses only upload-artifact, contents: read. So no tag, release, checksum or version note: true. Expiry (GitHub default 90 days) and login requirement for artifact download (true even on public repos) are from general knowledge, not checked live. I did not check whether the repo is public.
Consequence: a buyer of an assembled $399 unit gets nothing flashed-and-versioned unless the seller pre-flashes. A first-time buyer must hunt a green run, have a GitHub account, and may find the artifact expired and the run gone, the first time they need to reflash or the ini. Mismatch between ini and firmware is the real risk (ini must match the firmware version). It is an inconvenience, not a safety or hardware fault; "high" overstates. Medium.
R13.09 half is strategy advice (inferred), not a defect.
Not documented in review brief s6 or VERIFICATION open items. Does not affect ordered boards (firmware only).
Fix: cheap. Add a tag-triggered job using softprops/action-gh-release (or gh release) uploading bin/dfu/ini/bundle plus SHA256SUMS, per batch; pre-flash units at the seller. Minutes of work; no board change.
