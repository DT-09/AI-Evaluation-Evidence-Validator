from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "website" / "index.html"

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]
        self.fragments=[]
        self.title_text=False
        self.title=""
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get("id"): self.ids.append(attrs["id"])
        href=attrs.get("href","")
        if href.startswith("#") and len(href)>1: self.fragments.append(href[1:])
        if tag=="title": self.title_text=True
    def handle_endtag(self,tag):
        if tag=="title": self.title_text=False
    def handle_data(self,data):
        if self.title_text: self.title+=data

class PublicWebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=SITE.read_text(encoding="utf-8")
        cls.parser=SiteParser()
        cls.parser.feed(cls.html)
        cls.parser.close()
    def test_page_exists_and_has_title(self):
        self.assertTrue(SITE.is_file())
        self.assertIn("DealTie",self.parser.title)
    def test_required_sections_exist(self):
        required={"top","problem","workflow","demo","scope"}
        self.assertTrue(required.issubset(set(self.parser.ids)))
    def test_ids_are_unique(self):
        self.assertEqual(len(self.parser.ids),len(set(self.parser.ids)))
    def test_internal_navigation_targets_exist(self):
        ids=set(self.parser.ids)
        missing=sorted(set(self.parser.fragments)-ids)
        self.assertEqual(missing,[])
    def test_synthetic_demo_is_clearly_labelled(self):
        self.assertRegex(self.html,re.compile(r"synthetic",re.IGNORECASE))
        self.assertIn("not client data",self.html.lower())
    def test_product_boundaries_are_disclosed(self):
        for phrase in ("no scanned-pdf ocr","semantic matching","not an audit opinion","not proof of an error"):
            self.assertIn(phrase,self.html.lower())

if __name__=="__main__": unittest.main()
