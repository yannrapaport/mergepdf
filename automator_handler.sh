#!/bin/bash
#
# automator_handler.sh
# 
# Handler script for macOS Automator to merge odd and even PDF pages
# Works with Quick Action (formerly Service) workflows
#

# --- Configuration ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLI_SCRIPT="${SCRIPT_DIR}/merge_pdfs_cli.sh"
LOG_FILE="${SCRIPT_DIR}/logs/automator.log"

# --- Functions ---

# Show a dialog to the user
show_dialog() {
    local message="$1"
    local title="${2:-MergePDF}"
    local icon="${3:-note}"  # note, caution, stop
    
    osascript -e "display dialog \"$message\" buttons {\"OK\"} default button \"OK\" with icon $icon with title \"$title\""
}

# Show a dialog with multiple options
show_choice_dialog() {
    local message="$1"
    local title="${2:-MergePDF}"
    local default_button="${3:-Yes}"
    local buttons="${4:-\"Yes\", \"No\"}"
    
    osascript -e "set theChoice to button returned of (display dialog \"$message\" buttons {$buttons} default button \"$default_button\" with title \"$title\")"
}

# Log a message
log_message() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log the beginning of execution
log_message "Automator handler started with ${#@} arguments: $@"

# --- Validation ---

# Check if we have exactly 2 arguments
if [ $# -ne 2 ]; then
    show_dialog "Please select exactly two PDF files: one for odd pages and one for even pages." "MergePDF Error" "stop"
    log_message "Error: Expected 2 files, got $#"
    exit 1
fi

# Get the file paths
FILE1="$1"
FILE2="$2"

# Validate file extensions
if [[ ! "$FILE1" =~ \.pdf$ ]] && [[ ! "$FILE1" =~ \.PDF$ ]]; then
    show_dialog "First selected file is not a PDF: $(basename "$FILE1")" "MergePDF Error" "stop"
    log_message "Error: First file is not a PDF: $FILE1"
    exit 1
fi

if [[ ! "$FILE2" =~ \.pdf$ ]] && [[ ! "$FILE2" =~ \.PDF$ ]]; then
    show_dialog "Second selected file is not a PDF: $(basename "$FILE2")" "MergePDF Error" "stop"
    log_message "Error: Second file is not a PDF: $FILE2"
    exit 1
fi

# --- File Selection Dialog ---

# Ask which file contains odd pages
ORDER_CHOICE=$(osascript -e 'set theChoice to button returned of (display dialog "Which file contains the ODD pages (1,3,5...)?" buttons {"First File", "Second File", "Cancel"} default button "First File" with title "MergePDF")' 2>/dev/null)

# Check if user cancelled
if [ "$ORDER_CHOICE" == "Cancel" ] || [ -z "$ORDER_CHOICE" ]; then
    log_message "User cancelled operation"
    exit 0
fi

# Determine which file is odd and which is even based on user selection
if [ "$ORDER_CHOICE" == "First File" ]; then
    ODD_FILE="$FILE1"
    EVEN_FILE="$FILE2"
    log_message "User selected first file as odd pages: $(basename "$FILE1")"
else
    ODD_FILE="$FILE2"
    EVEN_FILE="$FILE1"
    log_message "User selected second file as odd pages: $(basename "$FILE2")"
fi

# --- Execute Merge ---

# Check if the CLI script exists
if [ ! -f "$CLI_SCRIPT" ] || [ ! -x "$CLI_SCRIPT" ]; then
    show_dialog "Error: CLI script not found or not executable.\nPlease ensure ${CLI_SCRIPT} exists and has execute permissions." "MergePDF Error" "stop"
    log_message "Error: CLI script not found or not executable: $CLI_SCRIPT"
    exit 1
fi

# Show progress dialog
osascript -e 'tell application "System Events" to display dialog "Merging PDF files...\n\nThis may take a moment." buttons {} giving up after 1 with title "MergePDF" with icon note' &
DIALOG_PID=$!

# Execute the merge command
log_message "Executing: $CLI_SCRIPT \"$ODD_FILE\" \"$EVEN_FILE\""
MERGE_OUTPUT=$("$CLI_SCRIPT" --quiet "$ODD_FILE" "$EVEN_FILE" 2>&1)
MERGE_STATUS=$?

# Kill the progress dialog
kill $DIALOG_PID 2>/dev/null

# Check if merge was successful
if [ $MERGE_STATUS -ne 0 ]; then
    show_dialog "Error merging PDFs:\n\n$MERGE_OUTPUT" "MergePDF Error" "stop"
    log_message "Error merging PDFs: $MERGE_OUTPUT"
    exit 1
fi

# Extract output path from output
OUTPUT_PATH=$(echo "$MERGE_OUTPUT" | grep "Result saved to:" | sed 's/.*Result saved to: //')

# Show success dialog
if [ -n "$OUTPUT_PATH" ] && [ -f "$OUTPUT_PATH" ]; then
    show_dialog "PDFs successfully merged!\n\nResult saved to:\n$OUTPUT_PATH" "MergePDF" "note"
    log_message "Success: Merged PDF saved to $OUTPUT_PATH"
    
    # Open the merged file
    open "$OUTPUT_PATH"
else
    show_dialog "PDFs were merged, but the output file location is unknown." "MergePDF" "caution"
    log_message "Warning: Output path not found in merge output: $MERGE_OUTPUT"
fi

exit 0

