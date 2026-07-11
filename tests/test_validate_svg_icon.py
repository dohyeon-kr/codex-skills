import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills/rounded-line-svg-icon-maker/scripts/validate_svg_icon.py"


class ValidateSvgIconTest(unittest.TestCase):
    def validate_bytes(self, data):
        with tempfile.NamedTemporaryFile("wb", suffix=".svg") as handle:
            handle.write(data)
            handle.flush()
            return subprocess.run(
                [sys.executable, str(VALIDATOR), handle.name],
                check=False,
                capture_output=True,
                text=True,
            )

    def validate(self, svg):
        return self.validate_bytes(svg.encode("utf-8"))

    def test_accepts_safe_outline_icon(self):
        result = self.validate(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 12h16"/></svg>'
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_event_handler(self):
        result = self.validate('<svg viewBox="0 0 24 24" fill="none" onload="alert(1)"/>')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("event handler", result.stdout)

    def test_rejects_animation(self):
        result = self.validate(
            '<svg viewBox="0 0 24 24" fill="none"><path id="shape"/>'
            '<animate href="#shape" attributeName="d" values="M0 0;M24 24"/></svg>'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden SVG element", result.stdout)

    def test_rejects_javascript_reference(self):
        result = self.validate(
            '<svg viewBox="0 0 24 24" fill="none"><a href="javascript:alert(1)"><path/></a></svg>'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local fragment", result.stdout)

    def test_rejects_relative_external_reference(self):
        result = self.validate(
            '<svg viewBox="0 0 24 24" fill="none"><use href="icon.svg#shape"/></svg>'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local fragment", result.stdout)

    def test_allows_local_fragment_reference(self):
        result = self.validate(
            '<svg viewBox="0 0 24 24" fill="none"><path id="shape" d="M4 12h16"/>'
            '<use href="#shape"/></svg>'
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_dtd(self):
        result = self.validate(
            '<!DOCTYPE svg [<!ENTITY x "unsafe">]>'
            '<svg viewBox="0 0 24 24" fill="none"><path id="&x;"/></svg>'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DTD", result.stdout)

    def test_rejects_utf16_dtd_before_xml_parsing(self):
        svg = (
            '<?xml version="1.0" encoding="UTF-16"?>'
            '<!DOCTYPE svg [<!ENTITY x "unsafe">]>'
            '<svg viewBox="0 0 24 24" fill="none"><path id="&x;"/></svg>'
        )

        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            with self.subTest(encoding=encoding):
                result = self.validate_bytes(svg.encode(encoding))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("UTF-8", result.stdout)

    def test_rejects_xml_stylesheet(self):
        result = self.validate(
            '<?xml-stylesheet type="text/css" href="https://example.com/icon.css"?>'
            '<svg viewBox="0 0 24 24" fill="none"><path d="M4 12h16"/></svg>'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stylesheet", result.stdout)


if __name__ == "__main__":
    unittest.main()
