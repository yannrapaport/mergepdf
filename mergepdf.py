import argparse
from PyPDF2 import PdfReader, PdfWriter

def main():
    parser = argparse.ArgumentParser(description="Fusionner des fichiers PDF impairs et pairs.")
    parser.add_argument('-i', '--impairs', help="Chemin du fichier PDF des pages impaires", required=False)
    parser.add_argument('-p', '--pairs', help="Chemin du fichier PDF des pages paires", required=False)
    parser.add_argument('-o', '--output', help="Chemin du fichier PDF de sortie", required=False, default="output.pdf")
    parser.add_argument('impairs_positional', nargs='?', help="Chemin du fichier PDF des pages impaires (positionnel)")
    parser.add_argument('pairs_positional', nargs='?', help="Chemin du fichier PDF des pages paires (positionnel)")

    args = parser.parse_args()

    # Déterminer les chemins des fichiers impairs et pairs
    impairs_path = args.impairs if args.impairs else args.impairs_positional
    pairs_path = args.pairs if args.pairs else args.pairs_positional

    if not impairs_path or not pairs_path:
        parser.error("Les chemins des fichiers impairs et pairs doivent être spécifiés.")

    # Lire les fichiers PDF
    pdf_impairs = PdfReader(impairs_path)
    pdf_pairs_inverses = PdfReader(pairs_path)

    # Réordonner les pages paires (inversées à l'origine)
    pages_pairs = list(reversed(pdf_pairs_inverses.pages))

    # Fusionner les pages en alternant une impaire et une paire
    writer = PdfWriter()
    for i in range(max(len(pdf_impairs.pages), len(pages_pairs))):
        if i < len(pdf_impairs.pages):
            writer.add_page(pdf_impairs.pages[i])
        if i < len(pages_pairs):
            writer.add_page(pages_pairs[i])

    # Exporter le fichier final fusionné
    with open(args.output, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    main()