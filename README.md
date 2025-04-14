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

### Quick Install (macOS)

1. Download the latest release:
   ```bash
   curl -L https://github.com/yannrapaport/mergepdf/archive/refs/heads/main.zip -o mergepdf.zip
   unzip mergepdf.zip
   cd mergepdf-main
   ```

2. Make the CLI script executable:
   ```bash
   chmod +x merge_pdfs_cli.sh
   ```

3. Set up the background service:
   ```bash
   # Create the service configuration
   cp com.yannrapaport.mergepdf-api.plist ~/Library/LaunchAgents/
   
   # Edit paths in the configuration to match your installation
   # (replace USERNAME with your macOS username)
   sed -i '' "s|/Users/yannrapaport|/Users/$USER|g" ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   
   # Start the service
   launchctl load ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```

4. Verify installation:
   ```bash
   curl http://localhost:8000/api/health
   ```
   
   You should see `{"status":"ok"}`

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

## Service Management

The PDF merging service runs in the background and starts automatically when you log in.

### Service Commands

```bash
# Check if service is running
curl http://localhost:8000/api/health

# Restart the service
launchctl unload ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
launchctl load ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist

# Stop the service
launchctl unload ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist

# View service logs
cat /path/to/mergepdf/logs/api_*.log
```

## macOS Finder Integration

MergePDF can be integrated into the macOS Finder context menu using Automator. This allows you to right-click on two PDF files and merge them directly.

For detailed setup instructions, see [README_AUTOMATOR.md](README_AUTOMATOR.md).

## System Requirements

* macOS 10.14 Mojave or newer
* bash shell
* curl (for API testing)

## For Developers

If you want to modify or contribute to the project:

### Development Setup

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

### Technical Requirements

* Python 3.6+
* PyPDF2 (PDF manipulation)
* FastAPI (API framework)
* Uvicorn (ASGI server)
* python-multipart (file upload handling)
* bash (for CLI script)

## License

This project is open source and available under the MIT License.
