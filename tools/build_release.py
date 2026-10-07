"""Build Lokal-STT-Portable-<version>.zip for NinjaOne from an app folder.

    py -3 build_release.py

Layout inside the zip (same as before):  Lokal-STT-Portable/<app files>
plus  Lokal-STT-Portable/_deploy/Lokal-STT.lnk  (prebuilt shortcut, see make-shortcut.vbs)
and   Lokal-STT-Portable/VERSION.txt
Files whose paths were too long to unpack into the app folder are taken from the source zip.
"""
import hashlib
import zipfile
from pathlib import Path

VERSION = "1.1"
NOTE = "DS2-Upload (Grundig/Olympus/Philips Diktate) - Frontend-Erweiterung, Server/EXE unveraendert"
BUILT = "2026-10-07"
PLAYGROUND = Path(r"C:\Users\alkasemh\Desktop\Playground")
APP = PLAYGROUND / f"Lokal-STT-Portable-{VERSION}"
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
    files = sorted(p for p in APP.rglob("*") if p.is_file())
    names = {PREFIX + p.relative_to(APP).as_posix() for p in files}

    with zipfile.ZipFile(SOURCE_ZIP) as src:
        src_entries = {i.filename.replace("\\", "/"): i for i in src.infolist() if not i.filename.endswith(("/", "\\"))}
    missing = sorted(n for n in src_entries if n.startswith(PREFIX) and n not in names
                     and not n.startswith(PREFIX + "_internal/frontend/"))
    print(f"app files: {len(files)}   taken from source zip (long paths): {len(missing)}")

    version_txt = (f"Lokal-STT-Portable {VERSION}\r\n{NOTE}\r\nBuild: {BUILT}\r\n"
                   f"EXE SHA-256: {sha256(APP / 'Lokal-STT-Portable.exe')}\r\n")

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for p in files:
            z.write(p, PREFIX + p.relative_to(APP).as_posix())
        with zipfile.ZipFile(SOURCE_ZIP) as src:
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
