import argparse
from PyPDF2 import PdfReader, PdfWriter

def merge_pdfs(odd_path, even_path, output_path):
    pdf_odd = PdfReader(odd_path)
    pdf_even = PdfReader(even_path)
    even_pages = list(reversed(pdf_even.pages))

    writer = PdfWriter()
    for i in range(max(len(pdf_odd.pages), len(even_pages))):
        if i < len(pdf_odd.pages):
            writer.add_page(pdf_odd.pages[i])
        if i < len(even_pages):
            writer.add_page(even_pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)

def main():
    parser = argparse.ArgumentParser(description="Merge odd and even PDF files.")
    parser.add_argument('-i', '--odd', help="Path to the odd pages PDF", required=False)
    parser.add_argument('-p', '--even', help="Path to the even pages PDF", required=False)
    parser.add_argument('-o', '--output', help="Path for the output merged PDF", required=False, default="output.pdf")
    parser.add_argument('odd_positional', nargs='?', help="Path to the odd pages PDF (positional)")
    parser.add_argument('even_positional', nargs='?', help="Path to the even pages PDF (positional)")

    args = parser.parse_args()

    # Determine file paths
    odd_path = args.odd if args.odd else args.odd_positional
    even_path = args.even if args.even else args.even_positional

    if not odd_path or not even_path:
        parser.error("Both odd and even PDF file paths must be specified.")

    merge_pdfs(odd_path, even_path, args.output)

if __name__ == "__main__":
    main()
