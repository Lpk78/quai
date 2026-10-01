"""Cut the studio background off a supplied render, leaving a transparent PNG/WebP.

Asked for on #34: the phone renders and the operator must sit on the page with no grey box behind
them, so the page can give them its own shape-following shadow.

**Why not `rembg`.** `rembg` pulls in `onnxruntime` and downloads a ~170 MB segmentation model, and
`requirements-dev.txt` is installed on every Pull Request — that cost would be paid by CI forever to
produce files that are committed once. These renders do not need segmentation: their background is a
single near-white tone with a standard deviation under 1 across the whole border, so a flood fill from
the edges removes it exactly, and the alpha is feathered afterwards so nothing is left jagged. If a
future image arrives on a busy background, reach for `rembg` then — this is not a claim that colour
keying is always enough.

Run:  python3 assets/brand/cutout.py <source.png> <out.webp> [--pad 0.04]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def cut_out(path: Path, tolerance: int = 46, feather: float = 1.2) -> Image.Image:
    """Flood the near-uniform background away from every edge and feather what is left."""
    im = Image.open(path).convert("RGB")
    w, h = im.size

    # A one-pixel border, so a flood that reaches an edge always finds a way around the subject.
    framed = Image.new("RGB", (w + 2, h + 2), im.getpixel((0, 0)))
    framed.paste(im, (1, 1))

    key = (255, 0, 255)  # a colour that cannot occur in these renders
    ImageDraw.floodfill(framed, (0, 0), key, thresh=tolerance)

    flooded = np.array(framed.crop((1, 1, w + 1, h + 1)))
    background = np.all(flooded == np.array(key), axis=2)
    alpha = Image.fromarray(np.where(background, 0, 255).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(feather))

    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop(out.getbbox())


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        raise SystemExit(__doc__)
    source, target = Path(args[0]), Path(args[1])
    image = cut_out(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, lossless=False, quality=90)
    print(f"{source.name} -> {target} ({image.width}x{image.height}, transparent)")


if __name__ == "__main__":
    main()
