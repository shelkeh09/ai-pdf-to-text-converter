from __future__ import annotations

from pathlib import Path
import shutil
import unittest

from pdf_to_txt_converter.converter import convert_path, extract_pdf_text


def build_simple_pdf(page_texts: list[str]) -> bytes:
    def escape_pdf_text(value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    objects: list[str] = []
    page_ids: list[int] = []
    font_id = 3
    next_object_id = 4

    for _ in page_texts:
        page_ids.append(next_object_id)
        next_object_id += 2

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>\nendobj\n")
    objects.append("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    for index, text in enumerate(page_texts):
        page_id = page_ids[index]
        content_id = page_id + 1
        escaped_text = escape_pdf_text(text)
        stream = (
            "BT\n"
            "/F1 12 Tf\n"
            "72 720 Td\n"
            f"({escaped_text}) Tj\n"
            "ET\n"
        )
        objects.append(
            f"{page_id} 0 obj\n"
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>\n"
            "endobj\n"
        )
        objects.append(
            f"{content_id} 0 obj\n<< /Length {len(stream.encode('utf-8'))} >>\nstream\n"
            f"{stream}"
            "endstream\nendobj\n"
        )

    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("utf-8")))
        pdf += obj

    xref_offset = len(pdf.encode("utf-8"))
    pdf += f"xref\n0 {len(offsets)}\n"
    pdf += "0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += (
        "trailer\n"
        f"<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    return pdf.encode("utf-8")


class ConverterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_tmp_root = Path(__file__).resolve().parent / ".tmp"
        self.workspace_tmp_root.mkdir(exist_ok=True)
        self.test_dir = self.workspace_tmp_root / self._testMethodName
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.test_dir.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extract_pdf_text_with_page_markers(self) -> None:
        source_pdf = self.test_dir / "sample.pdf"
        source_pdf.write_bytes(build_simple_pdf(["Alpha page", "Beta page"]))

        text, page_count = extract_pdf_text(source_pdf, add_page_markers=True)

        self.assertEqual(page_count, 2)
        self.assertIn("[Page 1]", text)
        self.assertIn("Alpha page", text)
        self.assertIn("[Page 2]", text)
        self.assertIn("Beta page", text)

    def test_convert_directory_recursively_preserves_structure(self) -> None:
        root = self.test_dir
        source_dir = root / "pdfs"
        nested_dir = source_dir / "nested"
        output_dir = root / "converted"
        nested_dir.mkdir(parents=True)

        (source_dir / "one.pdf").write_bytes(build_simple_pdf(["First file"]))
        (nested_dir / "two.pdf").write_bytes(build_simple_pdf(["Second file"]))

        results = convert_path(source_dir, output_path=output_dir, recursive=True)

        self.assertEqual(len(results), 2)
        first_output = output_dir / "one.txt"
        second_output = output_dir / "nested" / "two.txt"
        self.assertTrue(first_output.exists())
        self.assertTrue(second_output.exists())
        self.assertIn("First file", first_output.read_text(encoding="utf-8"))
        self.assertIn("Second file", second_output.read_text(encoding="utf-8"))

    def test_single_file_defaults_to_neighbor_txt(self) -> None:
        source_pdf = self.test_dir / "notes.pdf"
        source_pdf.write_bytes(build_simple_pdf(["Quick lookup text"]))

        results = convert_path(source_pdf)

        self.assertEqual(len(results), 1)
        output_path = source_pdf.with_suffix(".txt")
        self.assertTrue(output_path.exists())
        self.assertIn("Quick lookup text", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
