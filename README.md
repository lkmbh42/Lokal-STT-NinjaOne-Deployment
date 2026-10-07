# Lokal-STT 1.1 – NinjaOne Deployment Kit

**New in 1.1:** DS2 dictation files (Grundig Digta, Olympus/OM System, Philips) can be
uploaded and transcribed like MP3. The server/exe is unchanged; only the web interface
was extended (details: `Desktop\Playground\DS2-Support\README.md`).

| File | Purpose |
|---|---|
| `Lokal-STT-Portable-1.1.zip` | The app (1.77 GB) – incl. model, DS2 support, mic icon, prebuilt shortcut |
| `ninjaone-install.ps1` | Install **and** update script (Run As SYSTEM) |
| `ninjaone-uninstall.ps1` | Removal script (Run As SYSTEM) |
| `SHA256SUMS.txt` | Checksums of the zip and the exe |
| `tools\` | Rebuild the zip / the shortcut (only needed for a new version) |

Zip SHA-256: `61BB025D5918976E28E9DBA05592929E0D8417A6DBBC7A37A461C8E1BDF6D661`
(also hard-coded in `ninjaone-install.ps1` – a different zip is refused).

## Why new scripts?

PCs now run PowerShell in **Constrained Language Mode** (`__PSLockdownPolicy=4`), which
also applies to NinjaOne scripts running as SYSTEM. The previous scripts used blocked
calls (`Add-Type`, .NET methods, COM for the shortcut) and **will fail**. The new scripts use
only allowed commands: `tar.exe` to unpack, `Get-FileHash`, and a prebuilt shortcut that
is just copied. Tested under CLM on 2026-10-07 (install, update, wrong-zip refusal, uninstall).

## Rollout

1. Copy `Lokal-STT-Portable-1.1.zip` to `\\srv1\configurator$\Packages\` (keep the 1.0 zip).
   The share must allow **read for "Domain Computers"** (share + NTFS).
2. NinjaOne → your **Lokal-STT – Install** script → replace the whole content with the new
   `ninjaone-install.ps1`. Check the `$Source` line points to your share.
   Run As **System**, timeout **30 min**.
3. Same for **Lokal-STT – Uninstall** with the new `ninjaone-uninstall.ps1`.
4. **Test on one PC** (one that already has 1.0 = tests the update). Expected output:
   `Zip OK`, `EXE OK`, two `Shortcut:` lines, `Version: Lokal-STT-Portable 1.1`, exit code 0.
   Then open Lokal-STT from the Desktop icon: the upload box must say
   "(mp3, wav, m4a, mp4, flac, **ds2**)".
5. Roll out to the device group / policy.

**Note:** the update closes Lokal-STT if it is open on that PC (a running transcription is
cancelled) – roll out outside working hours or tell users. Transcripts and settings in
`%LOCALAPPDATA%\Lokal-STT-Portable` are kept.

## Troubleshooting

| Output | Cause |
|---|---|
| `FAILED: ... Copy-Item ... access denied` / path not found | Share permission for "Domain Computers" or wrong `$Source` |
| `Zip integrity check FAILED` | Wrong or incompletely copied zip on the share – copy it again |
| `Not enough disk space` | Needs 5 GB free on C: during install |
| Desktop icon starts old version | Another Lokal-STT copy is still running – close it, start again |
