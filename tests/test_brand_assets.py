"""`assets/brand/README.md` against the files it indexes, and the demo QR codes against the app.

The index is what turns a folder of images into evidence for sections 3 and 9 of the specification:
what each piece is, what it was used for, and which tool made it. An index naming a file that is not
there is worth less than no index, because it is believed.

The QR codes matter for a different reason. They are the only way to replay the demo from a clone —
`/login` reads the badge, `/app/scan` reads the label — and the strings they encode are asserted here
against the patterns the app actually applies, so that renaming an operator id or a parcel in the
manifest cannot silently strand the printed codes.

Decoding the images themselves needs a QR decoder, which is not a dependency of this project; those
checks skip when one is absent rather than being dropped. `HY-24` decoded both with
`opencv-python-headless` in a throwaway environment and recorded the result in the PR.

Run from the repository root:  python3 -m unittest discover tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"
INDEX = BRAND / "README.md"
TEXT = INDEX.read_text(encoding="utf-8")

# What each code must encode, and the file in the web app that has to agree with it.
QR_CODES = {
    "demo-qr-operator-badge.png": "QUAI:OPERATOR:QUAI-OP-7842",
    "demo-qr-parcel-label.png": "QUAI:BOX:QUAI-BOX-0001",
}


class TestTheIndexNamesFilesThatExist(unittest.TestCase):
    def test_every_art_file_it_names_is_there(self):
        for name in sorted(set(re.findall(r"`(art/[a-z0-9-]+\.webp)`", TEXT))):
            with self.subTest(name):
                self.assertTrue((BRAND / name).is_file(),
                                f"assets/brand/README.md names {name}, which does not exist")

    def test_every_art_file_that_is_there_is_named(self):
        """The other direction: an unindexed image is an image nobody can account for."""
        for path in sorted((BRAND / "art").glob("*.webp")):
            with self.subTest(path.name):
                self.assertIn(f"art/{path.name}", TEXT,
                              f"{path.name} is committed but not indexed in assets/brand/README.md")

    def test_the_abandoned_workflow_is_kept(self):
        """A route prepared and dropped is part of how the work went; deleting it tidies history."""
        self.assertTrue((BRAND / "higgsfield_workflow_not_used.txt").is_file())

    def test_the_brand_guide_pdf_is_still_absent_and_the_index_says_why(self):
        """`HY-24` asked for the 4.8 MB guide. `design.md` and
        `test_brand.test_the_heavy_brand_guide_pdf_is_not_in_the_repository` already forbid it, so it
        was left out and the reason written down rather than the older test weakened to admit it."""
        self.assertFalse((BRAND / "QUAI_brand_guide.pdf").is_file())
        self.assertIn("deliberately not committed", TEXT)


class TestTheToolAttribution(unittest.TestCase):
    """Section 9 asks which tools were used. Only the three confirmed ones may appear."""

    def test_it_names_the_two_tools_that_produced_something(self):
        self.assertIn("ChatGPT", TEXT)
        self.assertIn("Claude", TEXT)

    def test_it_says_higgsfield_was_not_used(self):
        # The file is kept as a prepared-and-abandoned route. The one thing that must never drift is
        # the claim that it produced something.
        self.assertIn("Nothing in QUAI was produced with Higgsfield.", TEXT)

    def test_it_records_the_hand_retouching(self):
        self.assertIn("retouched by hand after generation", TEXT)

    def test_it_names_no_other_tool(self):
        """A tool nobody confirmed is a tool nobody used."""
        for invented in ("Midjourney", "DALL", "Stable Diffusion", "Firefly", "Sora", "Runway",
                         "Leonardo", "Flux", "Ideogram", "Veo"):
            with self.subTest(invented):
                self.assertNotIn(invented, TEXT)


class TestTheDemoQrCodes(unittest.TestCase):
    def test_both_are_committed_as_png(self):
        for name in QR_CODES:
            with self.subTest(name):
                self.assertTrue((BRAND / "demo-qr" / name).is_file(),
                                f"{name} is what makes the demo replayable from a clone")

    def test_the_index_says_what_each_encodes_and_where_it_is_used(self):
        for name, encoded in QR_CODES.items():
            with self.subTest(name):
                self.assertIn(encoded, TEXT)
        self.assertIn("/login", TEXT)
        self.assertIn("/app/scan", TEXT)

    def test_the_badge_matches_what_login_accepts(self):
        """`web/src/pages/Login.jsx` and the manifest have to agree with the printed code."""
        login = (ROOT / "web" / "src" / "pages" / "Login.jsx").read_text(encoding="utf-8")
        manifest = (ROOT / "web" / "src" / "data" / "manifest.js").read_text(encoding="utf-8")
        pattern = re.search(r"CODE_PATTERN = /(.+?)/;", login).group(1)
        self.assertRegex(QR_CODES["demo-qr-operator-badge.png"], pattern.replace("\\/", "/"))
        card = re.search(r'OPERATOR_CARD_ID = "([^"]+)"', manifest).group(1)
        self.assertEqual(QR_CODES["demo-qr-operator-badge.png"], f"QUAI:OPERATOR:{card}")

    def test_the_label_matches_what_the_scan_screen_accepts(self):
        scan = (ROOT / "web" / "src" / "scan" / "scanCode.js").read_text(encoding="utf-8")
        manifest = (ROOT / "web" / "src" / "data" / "manifest.js").read_text(encoding="utf-8")
        pattern = re.search(r"const LABEL = /(.+?)/;", scan).group(1)
        self.assertRegex(QR_CODES["demo-qr-parcel-label.png"], pattern.replace("\\/", "/"))
        parcel = re.search(r'id: "(QUAI-BOX-[0-9]+)"', manifest).group(1)
        self.assertEqual(QR_CODES["demo-qr-parcel-label.png"], f"QUAI:BOX:{parcel}")

    def test_the_images_decode_to_those_strings(self):
        """The strongest check, and the one that needs a decoder this project does not depend on."""
        try:
            import cv2  # noqa: PLC0415
        except ImportError:
            self.skipTest("no QR decoder installed; `pip install opencv-python-headless` to run this")
        detector = cv2.QRCodeDetector()
        for name, expected in QR_CODES.items():
            with self.subTest(name):
                decoded, _, _ = detector.detectAndDecode(cv2.imread(str(BRAND / "demo-qr" / name)))
                self.assertEqual(decoded, expected)


if __name__ == "__main__":
    unittest.main()
