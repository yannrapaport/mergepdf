#!/bin/bash
#
# merge_pdfs_cli.sh
# CLI for merging odd and even PDFs through the merge PDF API
#

# Configuration
API_URL="http://localhost:8000"
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
OUTPUT_DIR="$HOME/Downloads"
OUTPUT_FILE="merged_${TIMESTAMP}.pdf"
SHOW_PROGRESS=true

# Function to print in color
print_color() {
    local color=$1
    local message=$2
    
    case $color in
        "red")     echo -e "\033[0;31m${message}\033[0m" ;;
        "green")   echo -e "\033[0;32m${message}\033[0m" ;;
        "yellow")  echo -e "\033[0;33m${message}\033[0m" ;;
        "blue")    echo -e "\033[0;34m${message}\033[0m" ;;
        "magenta") echo -e "\033[0;35m${message}\033[0m" ;;
        "cyan")    echo -e "\033[0;36m${message}\033[0m" ;;
        *)         echo "${message}" ;;
    esac
}

# Function to show progress spinner
show_spinner() {
    local message=$1
    local pid=$2
    local delay=0.1
    local spinstr='|/-\'
    
    if [ "$SHOW_PROGRESS" = false ]; then
        return
    fi
    
    tput civis  # Hide cursor
    while kill -0 $pid 2>/dev/null; do
        local temp=${spinstr#?}
        printf "\r[%c] %s" "$spinstr" "$message"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
    done
    printf "\r                                \r"
    tput cnorm  # Show cursor
}

# Function to display help
show_help() {
    echo "Usage: $(basename $0) [OPTIONS] ODD_PDF EVEN_PDF"
    echo
    echo "Merge odd and even pages from two PDF files using the MergePDF API."
    echo
    echo "Arguments:"
    echo "  ODD_PDF              Path to the PDF containing odd pages"
    echo "  EVEN_PDF             Path to the PDF containing even pages (in reversed order)"
    echo
    echo "Options:"
    echo "  -o, --output FILE    Specify output filename (default: merged_TIMESTAMP.pdf)"
    echo "  -d, --dir DIR        Specify output directory (default: ~/Downloads)"
    echo "  -q, --quiet          Disable progress indicators"
    echo "  -h, --help           Display this help message and exit"
    echo
    echo "Example:"
    echo "  $(basename $0) odd_pages.pdf even_pages.pdf"
    echo "  $(basename $0) -o my_document.pdf -d ~/Desktop odd_pages.pdf even_pages.pdf"
}

# Function to check if API is available
check_api() {
    curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health" | grep -q "200"
    local status=$?
    
    if [ $status -ne 0 ]; then
        print_color "red" "Error: MergePDF API is not available at $API_URL"
        print_color "yellow" "Make sure the API server is running."
        exit 1
    fi
}

# Parse command line options
while [ $# -gt 0 ]; do
    case "$1" in
        -o|--output)
            shift
            OUTPUT_FILE="$1"
            shift
            ;;
        -d|--dir)
            shift
            OUTPUT_DIR="$1"
            shift
            ;;
        -q|--quiet)
            SHOW_PROGRESS=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            print_color "red" "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            # Not an option, assume it's a positional argument
            break
            ;;
    esac
done

# Check if we have the required arguments
if [ $# -ne 2 ]; then
    print_color "red" "Error: Please provide exactly two PDF files."
    show_help
    exit 1
fi

ODD_PDF="$1"
EVEN_PDF="$2"
OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

# Validate input files
if [ ! -f "$ODD_PDF" ]; then
    print_color "red" "Error: Odd pages file not found: $ODD_PDF"
    exit 1
fi

if [ ! -f "$EVEN_PDF" ]; then
    print_color "red" "Error: Even pages file not found: $EVEN_PDF"
    exit 1
fi

if [[ ! "$ODD_PDF" =~ \.pdf$ ]] && [[ ! "$ODD_PDF" =~ \.PDF$ ]]; then
    print_color "red" "Error: Odd pages file must be a PDF: $ODD_PDF"
    exit 1
fi

if [[ ! "$EVEN_PDF" =~ \.pdf$ ]] && [[ ! "$EVEN_PDF" =~ \.PDF$ ]]; then
    print_color "red" "Error: Even pages file must be a PDF: $EVEN_PDF"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if API is available
check_api

# Step 1: Upload the files to the API
print_color "blue" "Uploading PDF files to the API..."

# Start the upload in the background
upload_output=$(mktemp)
(curl -s -X POST \
    "$API_URL/api/merge" \
    -F "odd_file=@$ODD_PDF" \
    -F "even_file=@$EVEN_PDF" \
    -F "output_filename=$OUTPUT_FILE" > "$upload_output") &

upload_pid=$!
show_spinner "Uploading and processing files" $upload_pid
wait $upload_pid
upload_status=$?

if [ $upload_status -ne 0 ]; then
    print_color "red" "Error: Failed to upload files to API"
    exit 1
fi

# Extract job_id from the response
JOB_ID=$(cat "$upload_output" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
rm "$upload_output"

if [ -z "$JOB_ID" ]; then
    print_color "red" "Error: Failed to get job ID from API response"
    cat "$upload_output"
    exit 1
fi

# Step 2: Download the merged PDF
print_color "blue" "Downloading merged PDF..."

# Download in the background to show progress
(curl -s -o "$OUTPUT_PATH" "$API_URL/api/download/$JOB_ID") &
download_pid=$!
show_spinner "Downloading merged PDF" $download_pid
wait $download_pid
download_status=$?

if [ $download_status -ne 0 ] || [ ! -f "$OUTPUT_PATH" ]; then
    print_color "red" "Error: Failed to download merged PDF"
    exit 1
fi

# Check file size to ensure it's a valid PDF
file_size=$(stat -f%z "$OUTPUT_PATH")
if [ "$file_size" -lt 100 ]; then
    print_color "red" "Error: Downloaded file appears to be invalid (too small)"
    exit 1
fi

# Success message
print_color "green" "✅ PDF files successfully merged!"
print_color "green" "📄 Result saved to: $OUTPUT_PATH"

# Open the file
if [ -f "$OUTPUT_PATH" ]; then
    open "$OUTPUT_PATH"
fi

exit 0

