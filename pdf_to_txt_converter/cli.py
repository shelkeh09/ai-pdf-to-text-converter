from __future__ import annotations

import argparse
from pathlib import Path

from .converter import convert_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-to-text",
        description="Convert PDF files into plain text documents for faster searching.",
    )
    parser.add_argument("source", type=Path, help="PDF file or folder containing PDF files")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output text file or output folder. Defaults to the source folder.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subfolders when the source is a directory.",
    )
    parser.add_argument(
        "--page-markers",
        action="store_true",
        help="Insert page headers like [Page 1] into the output text.",
    )
    parser.add_argument(
        "--page-template",
        default="[Page {page}]",
        help="Template used for page markers. Default: [Page {page}]",
    )
    parser.add_argument(
        "--keep-empty-pages",
        action="store_true",
        help="Keep empty page markers when a page has no extractable text.",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable whitespace cleanup in extracted text.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        results = convert_path(
            args.source,
            output_path=args.output,
            recursive=args.recursive,
            add_page_markers=args.page_markers,
            page_template=args.page_template,
            keep_empty_pages=args.keep_empty_pages,
            normalize_output=not args.no_normalize,
        )
    except (FileNotFoundError, ValueError) as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")

    total_pages = sum(result.page_count for result in results)
    total_characters = sum(result.character_count for result in results)

    for result in results:
        print(f"Converted: {result.source_path} -> {result.output_path}")

    print(
        f"Finished {len(results)} file(s), {total_pages} page(s), "
        f"{total_characters} character(s) written."
    )
    return 0
