# Lokal-STT 1.2 – NinjaOne Deployment Kit

**Just want to run it on one PC?** See **[RUN.md](RUN.md)** – download, unzip, double-click.
This README is for **mass deployment via NinjaOne**.

**New in 1.2:** DS2 **and DSS** dictation files (Grundig Digta, Olympus/OM System, Philips)
upload and transcribe like MP3, plus a reworked, accessible web interface (compact history
with search, in-browser editor improvements, dictionary CSV import/export). The server/exe is
unchanged – only the web interface was extended, so the **exe SHA-256 is identical to 1.1**
(details: `Desktop\Playground\DS2-Support\README.md`).

| File | Purpose |
|---|---|
| `Lokal-STT-Portable-1.2.zip` | The app (~1.8 GB) – incl. model, DS2/DSS support, prebuilt shortcut (GitHub **Release** asset, not in the repo) |
| `ninjaone-install.ps1` | Install **and** update script (Run As SYSTEM) |
| `ninjaone-uninstall.ps1` | Removal script (Run As SYSTEM) |
| `RUN.md` | Run it manually on a single PC (no installer) |
| `SHA256SUMS.txt` | Checksums of the zip and the exe |
| `tools\` | Rebuild the zip / the shortcut (only needed for a new version) |

Zip SHA-256: `624E68F04FF264A43CF21A0FF5A38484039E8D891D664141A2DCA0270392F587`
(also hard-coded in `ninjaone-install.ps1` – a different zip is refused.)
Exe SHA-256: `50148EAD01B7301A8BCF91D49ED549FBC5DA2AEC16DB4118E705BF22028BBF6D` (unchanged since 1.1).

## Why these scripts?

PCs run PowerShell in **Constrained Language Mode** (`__PSLockdownPolicy=4`), which also
applies to NinjaOne scripts running as SYSTEM. The scripts use only allowed commands:
`tar.exe` to unpack, `Get-FileHash`, and a prebuilt shortcut that is just copied.

## Rollout

1. Copy `Lokal-STT-Portable-1.2.zip` to `\\srv1\configurator$\Packages\` (keep the old zip
   until 1.2 is verified). The share must allow **read for "Domain Computers"** (share + NTFS).
2. NinjaOne → your **Lokal-STT – Install** script → replace the whole content with the new
   `ninjaone-install.ps1`. Check the `$Source` line points to your share.
   Run As **System**, timeout **30 min**.
3. Same for **Lokal-STT – Uninstall** with `ninjaone-uninstall.ps1`.
4. **Test on one PC** (one that already has an older version = tests the update). Expected
   output: `Zip OK`, `EXE OK`, two `Shortcut:` lines, `Version: Lokal-STT-Portable 1.2`,
   exit code 0. Then open Lokal-STT from the Desktop icon: the upload box must list
   **ds2, dss**, and the header must show **· 1.2**.
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

## Rebuild the zip (new version only)

```
py -3 tools\build_release.py --source <previous Lokal-STT-Portable zip>
```

Packages the patched build folder into `Lokal-STT-Portable-<version>.zip` and rewrites
`SHA256SUMS.txt`. Override the build folder with `--app <folder>` if needed.
