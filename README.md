# MergePDF

A tool to merge odd and even pages from separate PDF files into a single document. This is particularly useful when scanning double-sided documents using a single-sided scanner.

MergePDF provides multiple ways to merge your PDF files:

- **Command-line interface** with user-friendly progress indicators
- **REST API** for programmatic access and integration
- **macOS Finder integration** via Automator Quick Action

## Features

- Merge odd pages (1,3,5...) from one PDF with even pages (2,4,6...) from another
- Handle reversed even pages from single-sided scanners
- Visual progress indicators and native macOS notifications
- Simple API for integration with other tools
- Finder context menu integration

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
   pip install PyPDF2 fastapi uvicorn python-multipart
   ```

4. Make the CLI script executable:
   ```bash
   chmod +x merge_pdfs_cli.sh
   ```

5. Set up the API service (see "API Service Setup" section below)

## Command-Line Usage

The `merge_pdfs_cli.sh` script provides a user-friendly interface with progress indicators and descriptive feedback:

```bash
./merge_pdfs_cli.sh [OPTIONS] ODD_PDF EVEN_PDF
```

### Options:

* `-o, --output FILE`: Specify output filename (default: merged_TIMESTAMP.pdf)
* `-d, --dir DIR`: Specify output directory (default: ~/Downloads)
* `-q, --quiet`: Disable progress indicators
* `-h, --help`: Display help message

### Examples:

```bash
# Basic usage
./merge_pdfs_cli.sh odd_pages.pdf even_pages.pdf

# Specify output file and location
./merge_pdfs_cli.sh -o merged_document.pdf -d ~/Desktop odd_pages.pdf even_pages.pdf
```

## API Usage

For programmatic access, MergePDF provides a REST API that can be accessed locally.

### Starting the API manually (for testing):

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

### API Endpoints:

* `POST /api/merge`: Upload and merge two PDF files
* `GET /api/download/{job_id}`: Download the merged PDF
* `GET /api/health`: Check API health status

### Example using curl:

```bash
# Upload files to merge
JOB_ID=$(curl -s -X POST "http://localhost:8000/api/merge" \
  -F "odd_file=@odd_pages.pdf" \
  -F "even_file=@even_pages.pdf" \
  -F "output_filename=merged.pdf" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)

# Download the merged file
curl -o merged.pdf "http://localhost:8000/api/download/$JOB_ID"
```

## API Service Setup

To run the API service as a background process on macOS:

1. Edit the launchd service configuration:
   ```bash
   nano ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```
   
   Update paths to match your installation directory.

2. Load the service:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```

3. Verify the service is running:
   ```bash
   curl http://localhost:8000/api/health
   ```

This will start the API service automatically when you log in.

## macOS Finder Integration

MergePDF can be integrated into the macOS Finder context menu using Automator. This allows you to right-click on two PDF files and merge them directly.

For detailed setup instructions, see [README_AUTOMATOR.md](README_AUTOMATOR.md).

## Requirements

* Python 3.6+
* PyPDF2
* FastAPI
* Uvicorn
* python-multipart
* bash (for CLI script)
* macOS (for full Finder integration)

## License

This project is open source and available under the MIT License.
