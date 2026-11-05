import io
import unittest

from openpyxl import Workbook

from dealtie.extract import excel_col, extract_excel


class ExcelExtractionTests(unittest.TestCase):
    def make_workbook(self):
        workbook = Workbook()
        first = workbook.active
        first.title = "Operating Model"
        first["A1"] = "Revenue"
        first["C4"] = 128.4
        first["B7"] = "FY2025"
        second = workbook.create_sheet("QoE")
        second["D12"] = 126.9
        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    def test_excel_cells_keep_sheet_and_cell_references(self):
        extracted = extract_excel(self.make_workbook(), "sample.xlsx")
        by_ref = {item["source_ref"]: item["extracted_text"] for item in extracted}
        self.assertEqual(by_ref["Operating Model!A1"], "Revenue")
        self.assertEqual(by_ref["Operating Model!C4"], "128.4")
        self.assertEqual(by_ref["Operating Model!B7"], "FY2025")
        self.assertEqual(by_ref["QoE!D12"], "126.9")

    def test_empty_cells_are_not_extracted(self):
        extracted = extract_excel(self.make_workbook(), "sample.xlsx")
        refs = {item["source_ref"] for item in extracted}
        self.assertNotIn("Operating Model!B1", refs)
        self.assertNotIn("QoE!A1", refs)

    def test_excel_column_labels(self):
        self.assertEqual(excel_col(1), "A")
        self.assertEqual(excel_col(26), "Z")
        self.assertEqual(excel_col(27), "AA")
        self.assertEqual(excel_col(702), "ZZ")


if __name__ == "__main__":
    unittest.main()
