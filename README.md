# MergePDF

A Python utility to merge odd and even pages from separate PDF files into a single document. This is particularly useful when scanning double-sided documents using a single-sided scanner.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yannrapaport/mergepdf.git
   cd mergepdf
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install PyPDF2
   ```

## Usage

```bash
python mergepdf.py [-h] [-i ODD] [-p EVEN] [-o OUTPUT] [odd_positional] [even_positional]
```

### Arguments:

* `-i, --odd`: Path to the PDF file containing odd pages
* `-p, --even`: Path to the PDF file containing even pages
* `-o, --output`: Path to the output PDF file
* `odd_positional`: Path to odd pages PDF file (positional argument)
* `even_positional`: Path to even pages PDF file (positional argument)

### Example:

```bash
python mergepdf.py -i odd_pages.pdf -p even_pages.pdf -o merged_document.pdf
```

## Requirements

* Python 3
* PyPDF2

## License

This project is open source and available under the MIT License.
