# AI PDF to Text Converter

A small Python command-line tool that converts PDF files into plain `.txt` documents for faster searching, easier access, and lightweight text storage.

## Features

- Convert a single PDF or an entire folder of PDFs
- Preserve folder structure when converting directories
- Optional page markers for easier navigation in large text files
- Normalize extracted text to keep the output clean and searchable

## Project Structure

```text
pdf to txt converter/
|-- pdf_to_txt_converter/
|   |-- __init__.py
|   |-- __main__.py
|   |-- cli.py
|   `-- converter.py
|-- tests/
|   `-- test_converter.py
|-- pyproject.toml
|-- README.md
`-- requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Convert a single PDF:

```bash
python -m pdf_to_txt_converter "documents/report.pdf"
```

Convert a single PDF to a specific text file:

```bash
python -m pdf_to_txt_converter "documents/report.pdf" --output "output/report.txt"
```

Convert every PDF in a folder:

```bash
python -m pdf_to_txt_converter "documents" --output "converted_txt"
```

Convert PDFs recursively and add page markers:

```bash
python -m pdf_to_txt_converter "documents" --recursive --page-markers
```

## CLI Options

- `source`: PDF file or folder containing PDFs
- `-o, --output`: Output text file or output folder
- `-r, --recursive`: Search nested folders for PDFs
- `--page-markers`: Insert page headers like `[Page 1]`
- `--page-template`: Customize the page marker template
- `--keep-empty-pages`: Keep page separators even when a page has no extracted text
- `--no-normalize`: Disable whitespace cleanup

## Why This Project

PDFs are convenient for sharing, but plain text is often better for quick search, lightweight storage, and downstream text processing. This project focuses on turning document content into a simpler, searchable format without adding unnecessary complexity.

## Run Tests

```bash
python -m unittest discover -s tests -v
```
