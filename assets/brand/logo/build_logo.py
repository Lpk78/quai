"""Generate the three QUAI logo SVGs from one definition of the mark.

The mark is a loading dock read as a Q: a navy arch, a white dock opening seen in slight perspective, a
safety-orange parcel door inside it, and a ramp running down and to the right as the Q's tail. In the
lockup the mark is the Q, so the wordmark beside it spells `UAI`.

The letters are outlines, not live text, so the logo renders identically on a machine with no fonts
installed. The three files share these paths, so the app icon and the two lockups cannot drift apart —
`tests/test_brand.py` regenerates them into a temporary directory and fails if the committed files
differ.

Regenerate after editing:  python3 assets/brand/logo/build_logo.py
"""
import sys
from pathlib import Path

NAVY, WHITE, ORANGE = "#102238", "#FFFFFF", "#FF8A00"

# --- the mark, in its own 306 x 285 space -------------------------------------------------------
PORTAL = ("M0,108 A108,108 0 0 1 108,0 L180,0 A108,108 0 0 1 288,108 "
          "L288,204 A46,46 0 0 1 242,250 L46,250 A46,46 0 0 1 0,204 Z")
OPENING = "M66,92 Q66,70 88,74 L198,96 Q216,100 216,122 L216,210 L66,210 Z"
DOOR = "M94,116 Q94,98 110,101 L174,118 Q190,122 190,138 L190,206 L94,206 Z"
RAMP = "M66,204 L240,194 L308,264 L142,278 Z"

# --- the letters U A I, as outlines, cap height 238 on a baseline at y=268 -----------------------
U = ("M0,42 Q0,30 12,30 L50,30 Q62,30 62,42 L62,193 A13,13 0 0 0 88,193 L88,42 Q88,30 100,30 "
     "L138,30 Q150,30 150,42 L150,193 A75,75 0 0 1 0,193 Z")
A = ("M85,38 Q92,24 100,38 L185,258 Q189,268 178,268 L140,268 Q131,268 128,259 L116,228 L69,228 "
     "L57,259 Q54,268 45,268 L7,268 Q-4,268 0,258 Z"
     "M92,112 L112,174 L72,174 Z")
I = "M0,44 Q0,30 14,30 L48,30 Q62,30 62,44 L62,254 Q62,268 48,268 L14,268 Q0,268 0,254 Z"

LETTERS = [(U, 0), (A, 166), (I, 366)]   # x offsets; total width 428


def mark(arch: str, opening: str, door: str = ORANGE) -> str:
    """The mark. `arch` is the portal and the ramp; `opening` is the dock mouth behind the door."""
    return (f'<path d="{PORTAL}" fill="{arch}"/>'
            f'<path d="{OPENING}" fill="{opening}"/>'
            f'<path d="{DOOR}" fill="{door}"/>'
            f'<path d="{RAMP}" fill="{arch}" stroke="{arch}" stroke-width="14" '
            f'stroke-linejoin="round"/>')


def wordmark(colour: str) -> str:
    return "".join(f'<path d="{d}" fill="{colour}" fill-rule="evenodd" '
                   f'transform="translate({x} 0)"/>' for d, x in LETTERS)


def files() -> dict[str, str]:
    """Every logo file, as {name: svg}."""
    return {
        "quai-logo-light.svg":
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 790 300" width="790" '
            f'height="300" role="img" aria-label="QUAI">\n<title>QUAI</title>\n'
            f'<g transform="translate(8 6)">{mark(NAVY, WHITE)}</g>\n'
            f'<g transform="translate(344 10)">{wordmark(NAVY)}</g>\n</svg>\n',
        "quai-logo-dark.svg":
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 360" width="850" '
            f'height="360" role="img" aria-label="QUAI">\n<title>QUAI</title>\n'
            f'<rect width="850" height="360" rx="72" fill="{NAVY}"/>\n'
            f'<g transform="translate(38 36)">{mark(WHITE, NAVY)}</g>\n'
            f'<g transform="translate(374 40)">{wordmark(WHITE)}</g>\n</svg>\n',
        "quai-app-icon.svg":
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" '
            f'height="512" role="img" aria-label="QUAI">\n<title>QUAI</title>\n'
            f'<rect width="512" height="512" rx="114" fill="{NAVY}"/>\n'
            f'<g transform="translate(94 110) scale(1.06)">{mark(WHITE, NAVY)}</g>\n</svg>\n',
    }


def build(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in files().items():
        (out_dir / name).write_text(svg)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    build(target)
    print(f"wrote {len(files())} files to {target}")
