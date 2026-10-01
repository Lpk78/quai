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


def _to_path(mask, decimals=1):
    """Trace one mask into SVG path data, scaled back to 1x."""
    import numpy as np
    import potrace

    # potrace traces the *dark* areas, so the shape we want must be 0 and the rest 255. A 0/1 mask
    # traces as one solid rectangle, because potracer reads the array against a 0.5 black level.
    bmp = potrace.Bitmap(((~mask) * 255).astype(np.uint8))
    scale = 1.0 / UPSCALE
    out = []

    def pt(p):
        return f"{round(p.x * scale, decimals)},{round(p.y * scale, decimals)}"

    for curve in bmp.trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.2):
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
        paths = ([(_to_path(navy), NAVY), (_to_path(orange), ORANGE)] if kind == "light"
                 else [(_to_path(art), NAVY), (_to_path(white), WHITE), (_to_path(orange), ORANGE)])
        out[name] = _svg(box, paths)
    return out


def build(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in files().items():
        (out_dir / name).write_text(svg)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    build(target)
    print(f"traced {len(JOBS)} files into {target}")
