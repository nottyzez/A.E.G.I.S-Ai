"""
Unit and Integration Tests for Academic References and Poster QR Code Assets
"""

import os
import re
import sys
import subprocess
import unittest
import cv2
import numpy as np

TARGET_URL = "https://github.com/nottyzez/A.E.G.I.S-Ai/blob/main/REFERENCES.md"

CITATIONS = [
    (1, "Abu Sneineh, A., & Shabaneh, A.", "https://doi.org/10.1016/j.iot.2023.100789"),
    (2, "Alipio, M. I., Cruz, A. E. M., Doria, J. D. A., & Fruto, R. M. S.", "https://doi.org/10.1109/iThings.2019.00057"),
    (3, "Baltrušaitis, T., Ahuja, C., & Morency, L. P.", "https://doi.org/10.1109/TPAMI.2018.2798607"),
    (4, "Cakmak, I.", "https://doi.org/10.1002/jpln.200420485"),
    (5, "Elsherbiny, O., Fan, Y., Zhou, L., & Qiu, Z.", "https://doi.org/10.1016/j.compag.2022.107086"),
    (6, "Garg, D., Bansal, P., & Kumar, S.", "https://doi.org/10.1016/j.inffus.2024.102234"),
    (7, "Hu, J., Shen, L., & Sun, G.", "https://doi.org/10.1109/CVPR.2018.00745"),
    (8, "Koyama, H., Toda, T., & Hara, T.", "https://doi.org/10.1093/pcp/pce041"),
    (9, "Luan, M., Lan, W., & Sheng, X.", "https://doi.org/10.1093/pcp/pcac048"),
    (10, "Marschner, H.", "https://doi.org/10.1016/C2009-0-02393-4"),
    (11, "Masclaux-Daubresse, C., Daniel-Vedele, F., Dechorgnat, J., Chardon, F., Gaufichon, L., & Suzuki, A.", "https://doi.org/10.1093/aob/mcq028"),
    (12, "Meyer, G. E., & Neto, J. C.", "https://doi.org/10.1016/j.compag.2008.03.009"),
    (13, "Mitsanis, C., Tzerakis, C., & Savvas, D.", "https://doi.org/10.1016/j.atech.2024.100412"),
    (14, "Murugesan, R., Santhanam, K., & Ramasamy, M.", "https://doi.org/10.1038/s41598-024-84512-3"),
    (15, "Reyes-Yanes, A., Martinez, P., & Ahmad, R.", "https://doi.org/10.1016/j.compag.2022.106796"),
    (16, "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C.", "https://doi.org/10.1109/CVPR.2018.00474"),
    (17, "Selvaraju, R. R., Cogswell, M., Das, A., Vedaldi, A., Parikh, D., & Batra, D.", "https://doi.org/10.1109/ICCV.2017.74"),
    (18, "Tournaire-Roux, C., Sutka, M., Javot, H., Gout, E., Gerbeau, P., Luu, D. T., Bligny, R., & Maurel, C.", "https://doi.org/10.1038/nature01853"),
    (19, "Trejo-Téllez, L. I., & Gómez-Merino, F. C.", "https://doi.org/10.5772/37578"),
    (20, "Trong, N. H., Ghaffari, M., & Smith, P.", "https://doi.org/10.1109/ACCESS.2020.3013892"),
    (21, "Wang, Y., Sun, Z., & Chen, Y.", "https://doi.org/10.1016/j.scienta.2017.02.019"),
]

class TestAcademicReferencesAndQR(unittest.TestCase):
    def setUp(self):
        self.ref_file = "REFERENCES.md"
        self.readme_file = "README.md"
        self.qr_png = os.path.join("docs", "assets", "references_qr.png")
        self.qr_svg = os.path.join("docs", "assets", "references_qr.svg")
        self.qr_png_alias = os.path.join("assets", "references_qr.png")
        self.qr_svg_alias = os.path.join("assets", "references_qr.svg")

    def test_references_file_exists(self):
        """Verify REFERENCES.md exists at project root."""
        self.assertTrue(os.path.isfile(self.ref_file), "REFERENCES.md must exist at project root.")

    def test_references_contains_all_21_citations_with_clickable_links(self):
        """Verify all 21 numbered citations exist in REFERENCES.md with functional markdown links."""
        with open(self.ref_file, "r", encoding="utf-8") as f:
            content = f.read()

        for num, author, doi in CITATIONS:
            with self.subTest(citation_number=num, author=author):
                # Verify numbering
                self.assertRegex(
                    content,
                    rf"(?:^|\n){num}\.\s+",
                    f"Citation #{num} missing numbered prefix in REFERENCES.md"
                )
                # Verify author presence
                first_author = author.split(",")[0]
                self.assertIn(
                    first_author,
                    content,
                    f"First author {first_author} not found in citation #{num}"
                )
                # Verify DOI/URL presence
                self.assertIn(
                    doi,
                    content,
                    f"DOI {doi} not found in citation #{num}"
                )
                # Verify clickable markdown link structure
                link_pattern = rf"\[.*?\]\({re.escape(doi)}\)"
                self.assertRegex(
                    content,
                    link_pattern,
                    f"Clickable link for DOI {doi} not found in citation #{num}"
                )

    def test_readme_links_to_references(self):
        """Verify README.md includes a link or badge pointing to REFERENCES.md."""
        self.assertTrue(os.path.isfile(self.readme_file), "README.md must exist.")
        with open(self.readme_file, "r", encoding="utf-8") as f:
            readme_text = f.read()
        self.assertIn("REFERENCES.md", readme_text)
        self.assertRegex(readme_text, r"\[.*?\]\(REFERENCES\.md\)")

    def test_qr_code_asset_files_exist_and_dimensions(self):
        """Verify QR code assets exist in PNG and SVG formats with PNG >= 1000x1000 px."""
        for path in [self.qr_png, self.qr_png_alias]:
            with self.subTest(file=path):
                self.assertTrue(os.path.isfile(path), f"File {path} must exist.")
                img = cv2.imread(path)
                self.assertIsNotNone(img, f"Failed to load image at {path}")
                h, w = img.shape[:2]
                self.assertGreaterEqual(w, 1000, f"Width {w} must be >= 1000 px")
                self.assertGreaterEqual(h, 1000, f"Height {h} must be >= 1000 px")

        for path in [self.qr_svg, self.qr_svg_alias]:
            with self.subTest(file=path):
                self.assertTrue(os.path.isfile(path), f"File {path} must exist.")
                with open(path, "r", encoding="utf-8") as f:
                    svg_data = f.read()
                self.assertIn("<svg", svg_data)
                self.assertIn("</svg>", svg_data)

    def test_qr_code_decodes_to_exact_target_url(self):
        """Programmatically decode the QR code PNG and assert the target URL matches."""
        img = cv2.imread(self.qr_png)
        self.assertIsNotNone(img, f"Failed to read {self.qr_png}")
        detector = cv2.QRCodeDetector()
        decoded_url, points, _ = detector.detectAndDecode(img)
        self.assertEqual(
            decoded_url,
            TARGET_URL,
            f"Decoded QR URL '{decoded_url}' did not match target '{TARGET_URL}'"
        )

    def test_poster_sizing_and_placement_guidance_documented(self):
        """Verify sizing and placement recommendations for academic posters are documented."""
        guidelines_path = os.path.join("docs", "assets", "POSTER_GUIDELINES.md")
        self.assertTrue(os.path.isfile(guidelines_path), "POSTER_GUIDELINES.md must exist.")
        with open(guidelines_path, "r", encoding="utf-8") as f:
            text = f.read().lower()
        self.assertIn("quiet zone", text)
        self.assertIn("dpi", text)
        self.assertIn("placement", text)

    def test_qr_code_rotation_invariance(self):
        """Verify QR code can be decoded accurately under 90, 180, and 270 degree rotations."""
        img = cv2.imread(self.qr_png)
        self.assertIsNotNone(img, f"Failed to read {self.qr_png}")
        detector = cv2.QRCodeDetector()

        for rot in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
            with self.subTest(rotation_code=rot):
                rotated = cv2.rotate(img, rot)
                decoded_url, _, _ = detector.detectAndDecode(rotated)
                self.assertEqual(
                    decoded_url,
                    TARGET_URL,
                    f"Rotated QR code (code {rot}) failed to decode to target URL"
                )

    def test_qr_code_resilience_to_downscaling_and_blur(self):
        """Verify QR code decodes reliably under reasonable scaling and optical blur degradation."""
        img = cv2.imread(self.qr_png)
        self.assertIsNotNone(img, f"Failed to read {self.qr_png}")
        detector = cv2.QRCodeDetector()

        # Test downscaling to typical poster embedding sizes (800x800, 500x500)
        for size in [800, 500, 300]:
            with self.subTest(scale_size=size):
                resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
                decoded, _, _ = detector.detectAndDecode(resized)
                self.assertEqual(decoded, TARGET_URL, f"Downscaled QR {size}x{size} failed to decode.")

        # Test slight blur (e.g. 3x3 or 5x5 out-of-focus camera lens)
        for k in [3, 5]:
            with self.subTest(blur_kernel=k):
                blurred = cv2.GaussianBlur(img, (k, k), 0)
                decoded, _, _ = detector.detectAndDecode(blurred)
                self.assertEqual(decoded, TARGET_URL, f"Blurred QR (k={k}) failed to decode.")

    def test_svg_vector_module_parity(self):
        """Verify vector SVG path coordinates match raster PNG modules 100% with zero disparity."""
        with open(self.qr_svg, "r", encoding="utf-8") as f:
            svg_text = f.read()

        matches = re.findall(r"M(\d+),(\d+)h1v1h-1z", svg_text)
        self.assertGreater(len(matches), 0, "No module path commands found in SVG.")

        svg_matrix = np.ones((45, 45), dtype=np.uint8) * 255
        for c, r in matches:
            svg_matrix[int(r), int(c)] = 0

        png = cv2.imread(self.qr_png, cv2.IMREAD_GRAYSCALE)
        downsampled = cv2.resize(png, (45, 45), interpolation=cv2.INTER_NEAREST)
        diff = np.abs(svg_matrix.astype(int) - downsampled.astype(int)).max()
        self.assertEqual(diff, 0, "Disparity detected between vector SVG modules and raster PNG image.")

    def test_verification_script_execution(self):
        """Verify scripts/verify_references_and_qr.py executes standalone and exits with code 0."""
        script_path = os.path.join("scripts", "verify_references_and_qr.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        self.assertEqual(
            result.returncode,
            0,
            f"Verification script failed with exit code {result.returncode}:\n{result.stderr}\n{result.stdout}"
        )

if __name__ == "__main__":
    unittest.main()
