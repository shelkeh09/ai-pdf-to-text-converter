from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from pypdf import PdfReader


@dataclass(slots=True)
class ConversionResult:
    source_path: Path
    output_path: Path
    page_count: int
    character_count: int


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_pdf_text(
    pdf_path: Path,
    *,
    add_page_markers: bool = False,
    page_template: str = "[Page {page}]",
    keep_empty_pages: bool = False,
    normalize_output: bool = True,
) -> tuple[str, int]:
    reader = PdfReader(str(pdf_path))
    extracted_pages: list[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if normalize_output:
            text = normalize_text(text)
        else:
            text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

        if not text and not keep_empty_pages and not add_page_markers:
            continue

        if add_page_markers:
            marker = page_template.format(page=page_number)
            text = f"{marker}\n{text}".strip() if text else marker

        if text or keep_empty_pages:
            extracted_pages.append(text)

    combined_text = "\n\n".join(extracted_pages).strip()
    if combined_text:
        combined_text += "\n"

    return combined_text, len(reader.pages)


def iter_pdf_files(source_path: Path, recursive: bool = False) -> list[Path]:
    if source_path.is_file():
        if source_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {source_path}")
        return [source_path]

    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    if not source_path.is_dir():
        raise ValueError(f"Source path is not a file or directory: {source_path}")

    pattern = "**/*.pdf" if recursive else "*.pdf"
    files = sorted(source_path.glob(pattern))
    return [path for path in files if path.is_file()]


def resolve_output_path(source_file: Path, source_root: Path, output_path: Path | None) -> Path:
    if output_path is None:
        if source_root.is_file():
            return source_file.with_suffix(".txt")
        return source_root / "converted_txt" / source_file.relative_to(source_root).with_suffix(".txt")

    if source_root.is_file():
        if output_path.suffix.lower() == ".txt":
            return output_path
        return output_path / f"{source_file.stem}.txt"

    return output_path / source_file.relative_to(source_root).with_suffix(".txt")


def convert_pdf(
    source_file: Path,
    destination_file: Path,
    *,
    add_page_markers: bool = False,
    page_template: str = "[Page {page}]",
    keep_empty_pages: bool = False,
    normalize_output: bool = True,
    encoding: str = "utf-8",
) -> ConversionResult:
    text, page_count = extract_pdf_text(
        source_file,
        add_page_markers=add_page_markers,
        page_template=page_template,
        keep_empty_pages=keep_empty_pages,
        normalize_output=normalize_output,
    )
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    destination_file.write_text(text, encoding=encoding)

    return ConversionResult(
        source_path=source_file,
        output_path=destination_file,
        page_count=page_count,
        character_count=len(text),
    )


def convert_path(
    source_path: Path,
    *,
    output_path: Path | None = None,
    recursive: bool = False,
    add_page_markers: bool = False,
    page_template: str = "[Page {page}]",
    keep_empty_pages: bool = False,
    normalize_output: bool = True,
    encoding: str = "utf-8",
) -> list[ConversionResult]:
    pdf_files = iter_pdf_files(source_path, recursive=recursive)
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {source_path}")

    results: list[ConversionResult] = []
    for pdf_file in pdf_files:
        destination_file = resolve_output_path(pdf_file, source_path, output_path)
        result = convert_pdf(
            pdf_file,
            destination_file,
            add_page_markers=add_page_markers,
            page_template=page_template,
            keep_empty_pages=keep_empty_pages,
            normalize_output=normalize_output,
            encoding=encoding,
        )
        results.append(result)

    return results
