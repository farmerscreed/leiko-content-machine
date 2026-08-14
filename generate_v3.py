#!/usr/bin/env python3
"""Leiko card generator v3 — self-organizing.
Works even when all files are uploaded FLAT (no folders):
finds blank_1a/1b/1c.png and the template wherever they are,
rebuilds masters/ and fonts/, downloading fonts if absent.

Usage: python3 generate_v3.py copy_issueN.json out_issueN/
Requires: playwright (pip install playwright --break-system-packages; playwright install chromium)
"""
import hashlib, json, sys, pathlib, shutil, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
FONT_URLS = {
    "Archivo.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf",
    "SpaceGrotesk.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf",
    "InstrumentSerif-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf",
}

def find_all(name):
    """Every copy of a file across the search paths, deduped by content."""
    seen, hits = {}, []
    for base in [HERE, pathlib.Path.cwd(),
                 pathlib.Path("/mnt/user-data/uploads"),
                 pathlib.Path("/mnt/project"), pathlib.Path("/mnt/project-files")]:
        if base.exists():
            for p in base.rglob(name):
                if "masters" in p.parts and p.parent.name == "masters" and p.parent.parent == HERE:
                    continue                      # our own working copy
                d = hashlib.sha256(p.read_bytes()).hexdigest()
                if d not in seen:
                    seen[d] = p
                    hits.append(p)
    return hits


def find(name):
    """Locate a file: alongside this script, in cwd, in common upload mounts."""
    for base in [HERE, pathlib.Path.cwd(),
                 pathlib.Path("/mnt/user-data/uploads"),
                 pathlib.Path("/mnt/project"), pathlib.Path("/mnt/project-files")]:
        if base.exists():
            hits = list(base.rglob(name))
            if hits:
                return hits[0]
    return None

def setup():
    (HERE / "masters").mkdir(exist_ok=True)
    (HERE / "fonts").mkdir(exist_ok=True)
    for n in ["blank_1a.png", "blank_1b.png", "blank_1c.png"]:
        dst = HERE / "masters" / n
        if not dst.exists():
            cands = find_all(n)
            if not cands:
                sys.exit(f"MISSING master: {n} — upload it to the project files.")
            if len(cands) > 1:
                # Two different versions of a master is the one failure that
                # silently produces a wrong card: the old artwork still has a
                # BP reading painted on the watch, which the vision gate blocks.
                # Refuse to guess.
                lines = "\n".join(f"    {c}  sha {hashlib.sha256(c.read_bytes()).hexdigest()[:12]}"
                                   for c in cands)
                sys.exit(f"AMBIGUOUS master: found {len(cands)} DIFFERENT versions of {n}:\n"
                         f"{lines}\n"
                         "  Delete the old one(s). The correct master shows a blank, "
                         "switched-off watch screen — never a BP reading.")
            shutil.copy(cands[0], dst)
            print(f"master {n} <- {cands[0]}")
    for n, url in FONT_URLS.items():
        dst = HERE / "fonts" / n
        if not dst.exists():
            src = find(n)
            if src:
                shutil.copy(src, dst)
            else:
                print("downloading font:", n)
                urllib.request.urlretrieve(url, dst)
    tpl = HERE / "leiko_template_v2.html"
    if not tpl.exists():
        src = find("leiko_template_v2.html")
        if not src:
            sys.exit("MISSING leiko_template_v2.html — upload it to the project files.")
        shutil.copy(src, tpl)
    return tpl

def main(copy_path, outdir):
    # copy files and the template are UTF-8; Windows' default is the locale
    # codepage, so every read/write names the encoding or it crashes.
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    tpl_path = setup()
    doc = json.loads(pathlib.Path(copy_path).read_text(encoding="utf-8"))
    copy = doc["slots"] if "slots" in doc else doc   # v2 schema, or old flat file
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    tpl = tpl_path.read_text(encoding="utf-8")
    for k, v in copy.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    leftover = [t for t in ["STAT_A","STAT_MID","STAT_B","STAT_SUB","STAT_KICK","MYTH",
                            "FACT_HEAD","FACT_SUB","GIFT_HEAD1","GIFT_HEAD2","GIFT_BODY"]
                if "{{"+t+"}}" in tpl]
    if leftover:
        sys.exit(f"Copy file is missing slots: {leftover}")
    (HERE / "_filled.html").write_text(tpl, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        # as_uri() gives file:///C:/… on Windows; a hand-built f"file://{path}"
        # keeps the backslashes and Chromium refuses it.
        pg.goto((HERE / "_filled.html").as_uri())
        pg.wait_for_timeout(700)
        for el in pg.query_selector_all("[data-screen-label]"):
            lab = el.get_attribute("data-screen-label").replace(" ", "_")
            # both formats from the same render pass: PNG is what ingest sends
            # today (Facebook accepts it), JPEG is what Instagram requires.
            el.screenshot(path=str(out / f"leiko_{lab}.png"))
            el.screenshot(path=str(out / f"leiko_{lab}.jpg"), type="jpeg", quality=92)
            print("rendered", out / f"leiko_{lab}.png", "+ .jpg")
        b.close()
    print("DONE — 3 cards (PNG + JPEG) in", out)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python3 generate_v3.py copy_issueN.json out_dir/")
    main(sys.argv[1], sys.argv[2])
