#!/usr/bin/env python3
"""Generate Catppuccin archive icons (zip/tar/7z/gz/...) to match the folders.

Papirus draws nearly every archive mimetype through two real files:

    <size>/apps/ark.svg                           (35 mimetypes symlink here)
    <size>/mimetypes/application-x-compress.svg   (gzip/bzip/xz family)

Both only use five flat fills, so recoloring is a plain substitution. Colors
are read from the folder SVGs already in src/, so archives always match them.

usage: tools/gen-archive-icons.py [PAPIRUS_DIR]   (default /usr/share/icons/Papirus)
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
PAPIRUS = Path(sys.argv[1] if len(sys.argv) > 1 else "/usr/share/icons/Papirus")

SIZES = ["16x16", "22x22", "24x24", "32x32", "48x48", "64x64", "96x96", "128x128"]
ICONS = [("apps", "ark"), ("mimetypes", "application-x-compress")]

FLAVORS = ["latte", "frappe", "macchiato", "mocha"]
COLORS = ["rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach",
          "yellow", "green", "teal", "sky", "sapphire", "blue", "lavender"]

# Catppuccin overlay1, used for the zipper slider (Papirus #909090)
OVERLAY1 = {"latte": "#8C8FA1", "frappe": "#838BA7",
            "macchiato": "#8087A2", "mocha": "#7F849C"}


def fill_after(svg: str, marker: str) -> str:
    """fill color of the element whose attributes contain `marker`."""
    m = re.search(r'<\w+ style="[^"]*fill:(#[0-9A-Fa-f]{6})[^"]*"[^>]*' + re.escape(marker), svg)
    if not m:
        raise SystemExit(f"marker not found: {marker}")
    return m.group(1)


def mix(a: str, b: str, t: float) -> str:
    """linear mix of two #rrggbb colors, t=0 -> a, t=1 -> b."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def palette(flavor: str, color: str) -> dict:
    base = f"folder-cat-{flavor}-{color}"
    places = SRC / "64x64" / "places"
    folder = (places / f"{base}.svg").read_text()
    glyph = (places / f"{base}-download.svg").read_text()
    accent = fill_after(folder, 'x="4" y="21"')
    paper = fill_after(folder, 'x="8" y="16"')
    pull = re.search(r'<path style="fill:(#[0-9A-Fa-f]{6})" d="M 30,29', glyph).group(1)
    return {
        "#4caf50": accent,                  # box body / page
        "#88cc8b": mix(accent, paper, .4),  # dog-ear highlight (compress only)
        "#4b4b4b": pull,                    # zipper pull body
        "#909090": OVERLAY1[flavor],        # zipper slider
        "#ffffff": paper,                   # teeth + pull ring
    }


def recolor(svg: str, pal: dict) -> str:
    # one pass so a substituted value is never substituted again
    return re.sub(r"#[0-9A-Fa-f]{6}",
                  lambda m: pal.get(m.group(0).lower(), m.group(0)), svg)


def main() -> None:
    n = 0
    for flavor in FLAVORS:
        for color in COLORS:
            pal = palette(flavor, color)
            for size in SIZES:
                for sub, name in ICONS:
                    src = PAPIRUS / size / sub / f"{name}.svg"
                    if not src.is_file() or src.is_symlink():
                        continue
                    out = SRC / size / sub
                    out.mkdir(parents=True, exist_ok=True)
                    (out / f"{name}-cat-{flavor}-{color}.svg").write_text(
                        recolor(src.read_text(), pal))
                    n += 1
    print(f"wrote {n} icons")


if __name__ == "__main__":
    main()
