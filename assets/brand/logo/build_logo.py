"""Trace the three QUAI logo files from the approved sheet.

The first version of this script drew the mark by hand, from measurements taken off
`quai-logo-v2-sheet.png`. The review of #33 put the result next to the sheet and found the Q
distorted and the wordmark proportions off — a faithful generator reproducing the wrong shape. This
version does not draw anything: it separates each lockup on the sheet into its colour layers and
traces them, so the proportions are the sheet's rather than an estimate.

Each file is one crop of the sheet, so the three stay consistent by construction:

    light lockup   the navy ink and the orange door; the dock opening is transparent
    dark lockup    the navy plaque, then the white mark and wordmark, then the orange door
    app icon       the navy tile from the icon row, same layering

Regenerate after editing:  python3 assets/brand/logo/build_logo.py

Needs `numpy`, `pillow` and `potracer`, which are not in `requirements.txt`: they are build-time
tools for a brand asset, not runtime dependencies of QUAI. `tests/test_brand.py` skips its drift
check when they are absent and runs it when they are present.
"""
import sys
from pathlib import Path

NAVY, WHITE, ORANGE = "#102238", "#FFFFFF", "#FF8A00"
SHEET = Path(__file__).resolve().parent / "quai-logo-v2-sheet.png"
UPSCALE = 3  # trace at 3x and emit at 1x: smoother curves, identical proportions

# Crops on the sheet, found by locating the bands of ink rather than by eye.
JOBS = [
    ("quai-logo-light.svg", (281, 97, 1126, 377), "light"),
    ("quai-logo-dark.svg", (227, 424, 1221, 762), "dark"),
    ("quai-app-icon.svg", (380, 805, 590, 1011), "dark"),
    # The same dark lockup without its navy plaque: white mark and wordmark on transparency, for
    # placing on a navy surface that is already there (the band on the landing page). Keeping the
    # plaque would show its own traced edge against an identical navy.
    # Inset by 12 px so the plaque's own rounded edge falls outside the crop: those boundary pixels
    # are neither navy nor paper, so they would otherwise be traced as a white outline.
    ("quai-logo-on-navy.svg", (239, 436, 1209, 750), "on-navy"),
]


def _masks(box):
    """The colour layers of one crop, as boolean masks at UPSCALE."""
    import numpy as np
    from PIL import Image

    im = Image.open(SHEET).convert("RGB").crop(box)
    im = im.resize((im.width * UPSCALE, im.height * UPSCALE), Image.LANCZOS)
    a = np.array(im).astype(int)

    def near(colour, tol):
        return np.abs(a - np.array(colour)).sum(axis=2) < tol

    navy = near((16, 34, 56), 150)
    orange = near((255, 138, 0), 170) & ~navy
    paper = near((252, 252, 250), 90)          # the sheet's own background
    art = ~paper                                # everything that is part of the artwork
    return navy, orange, art & ~navy & ~orange, art


def _to_path(mask, decimals=1, turdsize=20):
    """Trace one mask into SVG path data, scaled back to 1x.

    `turdsize` is potrace's speckle filter, in pixels at UPSCALE. The default is enough for the two
    lockups and the icon, where every shape is large. The on-navy variant needs far more: its crop
    sits inside the navy plaque, so the sheet's own compression noise along that edge traces as a
    scatter of tiny white dots — a faint dotted frame around the logo, spotted in review on #34.
    """
    import numpy as np
    import potrace

    # potrace traces the *dark* areas, so the shape we want must be 0 and the rest 255. A 0/1 mask
    # traces as one solid rectangle, because potracer reads the array against a 0.5 black level.
    bmp = potrace.Bitmap(((~mask) * 255).astype(np.uint8))
    scale = 1.0 / UPSCALE
    out = []

    def pt(p):
        return f"{round(p.x * scale, decimals)},{round(p.y * scale, decimals)}"

    for curve in bmp.trace(turdsize=turdsize, alphamax=1.0, opticurve=True, opttolerance=0.2):
        out.append(f"M{pt(curve.start_point)}")
        for seg in curve:
            if seg.is_corner:
                out.append(f"L{pt(seg.c)}L{pt(seg.end_point)}")
            else:
                out.append(f"C{pt(seg.c1)} {pt(seg.c2)} {pt(seg.end_point)}")
        out.append("Z")
    return "".join(out)


def _svg(box, paths):
    width, height = box[2] - box[0], box[3] - box[1]
    body = "".join(f'<path d="{d}" fill="{c}" fill-rule="evenodd"/>' for d, c in paths if d)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="QUAI">\n'
        f"<title>QUAI</title>\n{body}\n</svg>\n"
    )


def files() -> dict[str, str]:
    """Every logo file, as {name: svg}."""
    out = {}
    for name, box, kind in JOBS:
        navy, orange, white, art = _masks(box)
        if kind == "light":
            paths = [(_to_path(navy), NAVY), (_to_path(orange), ORANGE)]
        elif kind == "on-navy":
            # The crop is inside the plaque, so anything that is neither navy nor orange is a white
            # letter. The usual `white` mask cannot be used: white letters are within tolerance of
            # the sheet's own paper colour and would be dropped as background.
            paths = [(_to_path(~(navy | orange), turdsize=600), WHITE),
                     (_to_path(orange, turdsize=600), ORANGE)]
        else:
            paths = [(_to_path(art), NAVY), (_to_path(white), WHITE), (_to_path(orange), ORANGE)]
        out[name] = _svg(box, paths)
    return out


def build(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in files().items():
        (out_dir / name).write_text(svg)


def record_fingerprint() -> str:
    """Write the hash of the sheet, this script and the four SVGs beside them.

    `tests/test_brand.py` compares it on every run and only re-traces when it no longer matches, so
    the six-second check costs nothing on the runs where nothing about the logo moved.
    """
    import hashlib

    here = Path(__file__).resolve().parent
    names = ["quai-logo-v2-sheet.png", "build_logo.py", *files()]
    digest = hashlib.sha256()
    for name in names:
        digest.update(f"logo/{name}".encode())
        digest.update((here / name).read_bytes())
    value = digest.hexdigest()
    (here / "traced.sha256").write_text(value + "\n")
    return value


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    build(target)
    print(f"traced {len(JOBS)} files into {target}")
    if target == Path(__file__).resolve().parent:
        print(f"fingerprint {record_fingerprint()[:16]}…")
