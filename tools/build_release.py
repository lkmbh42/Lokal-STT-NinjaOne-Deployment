"""Build Lokal-STT-Portable-<version>.zip for NinjaOne from an app folder.

    py -3 build_release.py [--source <zip>]

Layout inside the zip (same as before):  Lokal-STT-Portable/<app files>
plus  Lokal-STT-Portable/_deploy/Lokal-STT.lnk  (prebuilt shortcut, see make-shortcut.vbs)
and   Lokal-STT-Portable/VERSION.txt
A few files have paths too long to unpack into the app folder; they are copied from
the source zip (--source, default SOURCE_ZIP, or the previous release build).
"""
import argparse
import hashlib
import zipfile
from pathlib import Path

VERSION = "1.2"
NOTE = ("DS2/DSS-Upload (Grundig/Olympus/Philips Diktate) + ueberarbeitete Oberflaeche - "
        "reine Frontend-Erweiterung, Server/EXE unveraendert (EXE SHA-256 identisch zu 1.1)")
BUILT = "2026-11-10"
PLAYGROUND = Path(r"C:\Users\alkasemh\Desktop\Playground")
# The 1.2 frontend is applied in place to the 1.1 build folder, so the app folder keeps
# its 1.1 name; override with --app if it lives elsewhere.
APP = PLAYGROUND / "Lokal-STT-Portable-1.1"
SOURCE_ZIP = PLAYGROUND / "Steve" / "Lokal-STT-Portable.zip"  # the zip APP was unpacked from
KIT = Path(__file__).resolve().parent.parent
OUT = KIT / f"Lokal-STT-Portable-{VERSION}.zip"
SHORTCUT = KIT / "_build" / "Lokal-STT.lnk"
PREFIX = "Lokal-STT-Portable/"
INSTALL_BASE = r"C:\Program Files\Lokal-STT" + "\\"  # where the install script unpacks
MAX_PATH = 259


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SOURCE_ZIP,
                    help="zip supplying the few long-path files that can't live in the app folder")
    ap.add_argument("--app", type=Path, default=APP, help="app folder to package (default: the patched build)")
    args = ap.parse_args()
    source_zip = args.source
    app = args.app
    if not source_zip.is_file():
        raise SystemExit(f"source zip not found: {source_zip} (pass --source <zip>)")
    if not app.is_dir():
        raise SystemExit(f"app folder not found: {app} (pass --app <folder>)")

    files = sorted(p for p in app.rglob("*") if p.is_file())
    names = {PREFIX + p.relative_to(app).as_posix() for p in files}

    with zipfile.ZipFile(source_zip) as src:
        src_entries = {i.filename.replace("\\", "/"): i for i in src.infolist() if not i.filename.endswith(("/", "\\"))}
    # Long-path files that can't live in the app folder, pulled from the source zip.
    # Exclude the frontend (always taken from the app folder) and this script's own
    # build artifacts, so the source may be a raw app zip OR a previous release build.
    missing = sorted(n for n in src_entries if n.startswith(PREFIX) and n not in names
                     and not n.startswith(PREFIX + "_internal/frontend/")
                     and not n.startswith(PREFIX + "_deploy/")
                     and n != PREFIX + "VERSION.txt")
    print(f"app files: {len(files)}   taken from source zip (long paths): {len(missing)}")

    version_txt = (f"Lokal-STT-Portable {VERSION}\r\n{NOTE}\r\nBuild: {BUILT}\r\n"
                   f"EXE SHA-256: {sha256(app / 'Lokal-STT-Portable.exe')}\r\n")

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for p in files:
            z.write(p, PREFIX + p.relative_to(app).as_posix())
        with zipfile.ZipFile(source_zip) as src:
            for n in missing:
                z.writestr(PREFIX + n[len(PREFIX):], src.read(src_entries[n]), compress_type=zipfile.ZIP_DEFLATED)
        z.write(SHORTCUT, PREFIX + "_deploy/Lokal-STT.lnk")
        z.writestr(PREFIX + "VERSION.txt", version_txt)

    with zipfile.ZipFile(OUT) as z:
        bad = z.testzip()  # reads every entry and checks its CRC
        entries = [i.filename for i in z.infolist()]
        exe_hash = hashlib.sha256(z.read(PREFIX + "Lokal-STT-Portable.exe")).hexdigest().upper()
    if bad:
        raise SystemExit(f"CRC error in {bad}")

    longest = max(entries, key=len)
    full = INSTALL_BASE + longest.replace("/", "\\")
    print(f"entries: {len(entries)}   CRC check: OK")
    print(f"longest installed path: {len(full)} chars (limit {MAX_PATH}) -> {'OK' if len(full) <= MAX_PATH else 'TOO LONG'}")

    zip_hash = sha256(OUT)
    (KIT / "SHA256SUMS.txt").write_text(
        f"{zip_hash}  {OUT.name}\r\n{exe_hash}  {PREFIX}Lokal-STT-Portable.exe\r\n", encoding="ascii")
    print(f"zip: {OUT.name}  {OUT.stat().st_size / 2**20:.1f} MiB")
    print(f"zip SHA-256: {zip_hash}")
    print(f"exe SHA-256: {exe_hash}")


if __name__ == "__main__":
    main()
