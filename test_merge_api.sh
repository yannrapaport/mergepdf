#!/bin/bash
#
# Simple test script for the PDF merge API using existing scan files
#

# Find the scan files in Downloads directory
SCAN_FILES=($HOME/Downloads/Scan*.pdf)

if [ ${#SCAN_FILES[@]} -lt 2 ]; then
  echo "Error: Need at least 2 scan files in ~/Downloads/Scan*.pdf"
  echo "Found: ${SCAN_FILES[*]}"
  exit 1
fi

# Use the first two scan files for testing
ODD_FILE="${SCAN_FILES[0]}"
EVEN_FILE="${SCAN_FILES[1]}"

echo "Testing PDF merge with:"
echo "Odd pages file: $ODD_FILE"
echo "Even pages file: $EVEN_FILE"
echo

# Test the CLI script
echo "=== Testing merge_pdfs_cli.sh ==="
./merge_pdfs_cli.sh "$ODD_FILE" "$EVEN_FILE"

echo 
echo "Testing complete!"
echo "Check your Downloads folder for the merged PDF result."

