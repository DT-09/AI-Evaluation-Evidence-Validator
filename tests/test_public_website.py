from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


SITE = Path(__file__).resolve().parents[1] / "website" / "index.html"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.title_text = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        href = attrs.get("href", "")
        if href.startswith("#") and len(href) > 1:
            self.fragments.append(href[1:])
        if tag == "title":
            self.title_text = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.title_text = False

    def handle_data(self, data):
        if self.title_text:
            self.title += data


class PublicWebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = SITE.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.html)
        cls.parser.close()

    def test_page_exists_and_has_title(self):
        self.assertTrue(SITE.is_file())
        self.assertIn("AI Acceptance Assurance", self.parser.title)

    def test_required_sections_exist(self):
        required = {
            "home", "approach", "workflow", "demonstration",
            "scope", "protocol", "contact"
        }
        self.assertTrue(required.issubset(set(self.parser.ids)))

    def test_ids_are_unique(self):
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)))

    def test_internal_navigation_targets_exist(self):
        ids = set(self.parser.ids)
        missing = sorted(set(self.parser.fragments) - ids)
        self.assertEqual(missing, [])

    def test_synthetic_demo_is_clearly_labelled(self):
        self.assertRegex(self.html, re.compile(r"synthetic", re.IGNORECASE))
        self.assertIn("not customer data", self.html.lower())

    def test_product_boundaries_are_disclosed(self):
        for phrase in (
            "does not connect to or execute the live system",
            "No production monitoring",
            "No general semantic correctness",
            "not a certification",
        ):
            self.assertIn(phrase.lower(), self.html.lower())


if __name__ == "__main__":
    unittest.main()
