"""The brand tokens and the rules `documentation/design.md` states about them.

`design.md` is where the design system is written down; this file is what makes its accessibility
section fail the build when it stops being true. A token edited without rechecking its contrast, or a
white-on-orange button copied back out of the mockups, breaks a test here rather than reaching a phone.

Run from the repository root:  python3 -m unittest discover tests
"""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"
TOKENS = json.loads((BRAND / "tokens.json").read_text())
DESIGN = (ROOT / "documentation" / "design.md").read_text()

# Read from the tokens, never hardcoded: the contrast rules below are only a guarantee about the
# palette if they are computed from the same file the interface will be built from.
NAVY = TOKENS["colors"]["navy"]          # the only text colour allowed on orange
WHITE = TOKENS["colors"]["surface"]
DARK_ORANGE = "#C2410C"                  # orange as *text*; not a brand token, a derived one

# WCAG 2.1: body text needs 4.5:1, text at 24px (or 19px bold) and above needs 3:1.
AA_SMALL = 4.5
AA_LARGE = 3.0


def relative_luminance(colour: str) -> float:
    """WCAG 2.1 relative luminance of an #RRGGBB colour."""
    channels = [int(colour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    """WCAG 2.1 contrast ratio between two colours, from 1:1 to 21:1."""
    high, low = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TestContrastFormula(unittest.TestCase):
    """The ratios below are only worth trusting if the formula is right."""

    def test_black_on_white_is_the_maximum(self):
        self.assertAlmostEqual(contrast("#000000", "#FFFFFF"), 21.0, places=2)

    def test_a_colour_against_itself_is_the_minimum(self):
        self.assertAlmostEqual(contrast("#FF8A00", "#FF8A00"), 1.0, places=6)

    def test_the_order_of_the_arguments_does_not_matter(self):
        self.assertAlmostEqual(contrast("#1F2937", "#F7F6F3"), contrast("#F7F6F3", "#1F2937"))


class TestTokens(unittest.TestCase):
    def test_the_core_colours_are_the_ones_design_md_documents(self):
        colours = TOKENS["colors"]
        self.assertEqual(colours["background"], "#F7F6F3")
        self.assertEqual(colours["surface"], "#FFFFFF")
        self.assertEqual(colours["text"], "#1F2937")
        self.assertEqual(colours["navy"], "#102238")
        self.assertEqual(colours["primary_safety_orange"], "#FF8A00")

    def test_navy_is_a_token_and_not_only_a_rule_in_prose(self):
        """It is the mandatory text colour on orange, so it has to reach the interface as a token."""
        self.assertIn("navy", TOKENS["colors"])
        for colour in TOKENS["colors"].values():
            if isinstance(colour, str):
                with self.subTest(colour):
                    self.assertRegex(colour, r"^#[0-9A-F]{6}$")

    def test_the_three_fonts_are_the_ones_design_md_documents(self):
        for font in ("Plus Jakarta Sans", "Inter", "JetBrains Mono"):
            with self.subTest(font):
                self.assertIn(font, " ".join(TOKENS["typography"].values()))
                self.assertIn(font, DESIGN)

    def test_there_is_one_colour_per_delivery_stop_and_they_are_distinct(self):
        stops = TOKENS["colors"]["delivery_stops"]
        self.assertEqual(len(stops), 4)
        self.assertEqual(len(set(stops)), 4)


class TestReadableText(unittest.TestCase):
    """Everything the operator actually reads has to clear AA."""

    def setUp(self):
        self.background = TOKENS["colors"]["background"]
        self.surface = TOKENS["colors"]["surface"]
        self.text = TOKENS["colors"]["text"]

    def test_body_text_on_the_background(self):
        self.assertGreaterEqual(contrast(self.text, self.background), AA_SMALL)

    def test_body_text_on_a_card(self):
        self.assertGreaterEqual(contrast(self.text, self.surface), AA_SMALL)

    def test_navy_on_the_background(self):
        self.assertGreaterEqual(contrast(NAVY, self.background), AA_SMALL)


class TestTextOnOrange(unittest.TestCase):
    """First accessibility rule: text on orange is navy, never white."""

    def setUp(self):
        self.orange = TOKENS["colors"]["primary_safety_orange"]

    def test_navy_on_orange_passes_at_any_size(self):
        self.assertGreaterEqual(contrast(NAVY, self.orange), AA_SMALL)

    def test_white_on_orange_fails_even_at_large_sizes(self):
        # Not an accident to be fixed by loosening this: the mockups in
        # assets/brand/reference/mobile-ui.png show white on orange, and this is what forbids it.
        self.assertLess(contrast(WHITE, self.orange), AA_LARGE)

    def test_navy_beats_white_on_orange(self):
        self.assertGreater(contrast(NAVY, self.orange), contrast(WHITE, self.orange))

    def test_design_md_states_the_rule(self):
        self.assertIn("Text on orange is navy", DESIGN)


class TestOrangeAsText(unittest.TestCase):
    """Second accessibility rule: small orange text uses #C2410C, not the primary orange."""

    def setUp(self):
        self.background = TOKENS["colors"]["background"]
        self.orange = TOKENS["colors"]["primary_safety_orange"]

    def test_the_primary_orange_is_not_readable_as_text(self):
        self.assertLess(contrast(self.orange, self.background), AA_SMALL)

    def test_the_dark_orange_is_readable_as_text(self):
        self.assertGreaterEqual(contrast(DARK_ORANGE, self.background), AA_SMALL)

    def test_design_md_names_the_replacement(self):
        self.assertIn(DARK_ORANGE, DESIGN)


class TestFillOnlyColours(unittest.TestCase):
    """Status and stop colours are fills. design.md says so; this is why."""

    def test_the_status_colours_are_not_body_text_colours(self):
        background = TOKENS["colors"]["background"]
        for name in ("success", "warning", "error"):
            with self.subTest(name):
                self.assertLess(contrast(TOKENS["colors"][name], background), AA_SMALL)

    def test_design_md_warns_that_they_are_fills(self):
        self.assertIn("fill and icons only", DESIGN)

    def test_design_md_requires_a_second_channel_for_stop_colours(self):
        self.assertIn("Colour is a second channel, never the only one.", DESIGN)


class TestBrandFiles(unittest.TestCase):
    def test_the_logo_and_the_icon_are_present_as_vectors(self):
        for name in ("quai-logo-light.svg", "quai-logo-dark.svg", "quai-app-icon.svg"):
            with self.subTest(name):
                self.assertTrue((BRAND / "logo" / name).is_file())

    def test_the_wordmark_is_outlines_and_not_live_text(self):
        # The logo must render identically on a machine with no fonts installed. A <text> element
        # or a font-family would make the wordmark depend on what the viewer happens to have.
        for name in ("quai-logo-light.svg", "quai-logo-dark.svg", "quai-app-icon.svg"):
            with self.subTest(name):
                svg = (BRAND / "logo" / name).read_text()
                self.assertNotIn("<text", svg)
                self.assertNotIn("font-family", svg)

    def test_the_logo_is_vector_only(self):
        for name in ("quai-logo-light.svg", "quai-logo-dark.svg", "quai-app-icon.svg"):
            with self.subTest(name):
                svg = (BRAND / "logo" / name).read_text()
                self.assertNotIn("<image", svg)      # no raster smuggled into the vector
                self.assertNotIn("base64", svg)

    def test_the_logo_uses_the_brand_colours(self):
        svg = (BRAND / "logo" / "quai-logo-light.svg").read_text()
        self.assertIn(TOKENS["colors"]["primary_safety_orange"], svg)
        self.assertIn(NAVY, svg)

    def test_the_committed_svgs_match_their_generator(self):
        """design.md says the three files are traced from the sheet. This is what makes that true.

        The person this guards against is the one who opens `quai-logo-light.svg`, nudges a path by
        hand and commits it *instead of* running the generator — so they did not run the tracer and
        may not have it installed. Skipping where the tracer is absent would turn the check off in
        exactly that case, which is why `requirements-dev.txt` exists and why `tests.yml` installs
        it: this runs on every Pull Request, for everyone.
        """
        missing = [m for m in ("numpy", "PIL", "potrace") if importlib.util.find_spec(m) is None]
        self.assertEqual(missing, [],
                         "install requirements-dev.txt: the logo drift check needs the tracer")

        spec = importlib.util.spec_from_file_location(
            "build_logo", BRAND / "logo" / "build_logo.py")
        build_logo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_logo)
        with tempfile.TemporaryDirectory() as tmp:
            build_logo.build(Path(tmp))
            for name in build_logo.files():
                with self.subTest(name):
                    self.assertEqual((Path(tmp) / name).read_text(),
                                     (BRAND / "logo" / name).read_text(),
                                     f"{name} was edited by hand; re-run build_logo.py instead")

    def test_the_retired_logo_rasters_are_gone(self):
        # Two earlier marks were drawn before this one. Keeping a retired logo next to the live one
        # is how the wrong logo ends up shipped.
        for name in ("quai-app-icon.png", "quai-logo-variations.png"):
            with self.subTest(name):
                self.assertFalse((BRAND / "logo" / name).exists())

    def test_design_md_states_the_one_slogan(self):
        self.assertIn("People talk. We load.", DESIGN)

    def test_design_md_forbids_claiming_the_ai_plans_the_load(self):
        self.assertIn("Never say the AI plans the load or orders the stops", DESIGN)

    def test_every_brand_file_design_md_names_exists(self):
        """design.md points at files by name; renaming one without the other is the easy mistake."""
        named = set(re.findall(r"`(?:assets/brand/)?((?:logo|reference)/[\w.-]+\.(?:svg|png|jpg|json|py))`",
                               DESIGN))
        self.assertGreater(len(named), 8, "the reference list in design.md looks truncated")
        for rel in sorted(named):
            with self.subTest(rel):
                self.assertTrue((BRAND / rel).is_file(), f"design.md names {rel}, which does not exist")

    def test_no_reference_image_is_oversized(self):
        """Mood sheets are stored as JPEG, so none of them should be heavy.

        `master-brand-board.png` is the one exception, and it is exempt for a reason rather than
        because it is awkward: it is the kit's own declared source of truth, and it is read rather
        than looked at — the swatch labels and the type specimens on it are small print that JPEG
        ringing would make unreliable. Everything else in this folder is mood and layout, where
        lossy costs nothing. A new file does not get added to this exemption; it gets converted.
        """
        limit = 1_200_000
        exempt = {"master-brand-board.png"}
        too_big = [p.relative_to(BRAND).as_posix() for p in (BRAND / "reference").iterdir()
                   if p.is_file() and p.stat().st_size > limit and p.name not in exempt]
        self.assertEqual(too_big, [], "store these as JPEG, as design.md explains")

    def test_the_heavy_brand_guide_pdf_is_not_in_the_repository(self):
        self.assertEqual(list(ROOT.rglob("*.pdf")), [])


if __name__ == "__main__":
    unittest.main()
