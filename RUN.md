# Lokal-STT – run it on a PC (no installer)

Short guide to download and run Lokal-STT **1.2** on any Windows 10/11 (64-bit) PC.
No admin rights needed. Everything runs locally; no internet is required to use it.

## 1. Download

1. Open the repository on GitHub → **Releases** → **Lokal-STT-Portable 1.2**.
2. Download **`Lokal-STT-Portable-1.2.zip`** (~1.8 GB).

Or, if you have the GitHub CLI:

```bash
gh release download v1.2 --repo lkmbh42/Lokal-STT-NinjaOne-Deployment --pattern "*.zip"
```

## 2. Unzip

Right-click the zip → **Extract All…** (or use 7-Zip) into any folder, e.g. your Desktop.
You get a folder **`Lokal-STT-Portable`** (~2.5 GB). Keep all files together.

> If Windows shows a "blocked file" warning: right-click the **zip** → **Properties** →
> tick **Unblock** → **OK**, then extract.

## 3. Start

Double-click **`Lokal-STT-Portable\Lokal-STT-Portable.exe`**.

- The first start takes a few seconds (it loads the speech model).
- Your **browser opens automatically** at `http://127.0.0.1:48273` and you are **already
  signed in** – no password to type.
- If a blue **"Windows protected your PC"** box appears (the app is not code-signed):
  **More info → Run anyway**.

That's it – drag an audio or dictation file onto the upload box to transcribe it.

## 4. Stop

The app runs in the background with **no window**. To stop it:
**Task Manager** (Ctrl+Shift+Esc) → find **`Lokal-STT-Portable.exe`** → **End task**.

Starting the exe again just re-opens the browser (it never runs twice).

## Where your data is

Recordings, transcripts, settings and the local database are stored only on this PC, under:

```
%LOCALAPPDATA%\Lokal-STT-Portable
```

Deleting the `Lokal-STT-Portable` program folder does **not** delete that data; remove the
folder above as well if you want a clean slate.

## Verify the download (optional)

```powershell
Get-FileHash .\Lokal-STT-Portable-1.2.zip -Algorithm SHA256
```

The hash must match the `Lokal-STT-Portable-1.2.zip` line in **`SHA256SUMS.txt`**.

## Notes

- **Mass deployment** (many PCs via NinjaOne) uses `ninjaone-install.ps1` instead – see
  `README.md`.
- Supported uploads: mp3, wav, m4a, mp4, flac, **ds2**, **dss**.
- Needs ~5 GB free disk during first use.
