# MergePDF

macOS tool for merging odd/even pages from two separate PDF scans into a single document. Designed for single-sided scanner workflows.

## Dev Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install PyPDF2 fastapi uvicorn python-multipart watchdog
```

## Run

```bash
# API server
python -m uvicorn api:app --host 127.0.0.1 --port 8000

# CLI (direct, no API needed)
python mergepdf.py odd.pdf even.pdf -o output.pdf

# CLI (via API)
./merge_pdfs_cli.sh odd.pdf even.pdf

# Folder monitor (watches for new scans and auto-merges)
python folder_monitor.py --watch-dir ~/Downloads
```

## Test

```bash
./test_merge_api.sh  # requires Scan*.pdf files in ~/Downloads
```

## Key Files

- `mergepdf.py` — Core logic: `merge_pdfs(odd_path, even_path, output_path)` reverses even pages and interleaves with odd
- `api.py` — FastAPI REST API (POST `/api/merge`, GET `/api/download/{job_id}`, GET `/api/health`)
- `merge_pdfs_cli.sh` — Bash CLI wrapper (calls API via curl, requires API running)
- `automator_handler.sh` — macOS Finder Quick Action integration
- `folder_monitor.py` — Watches a folder for new PDFs and auto-merges consecutive pairs with similar page counts
- `com.mergepdf.folder-monitor.plist` — launchd service config for folder monitor

## Service Management

```bash
# Folder monitor service
cp com.mergepdf.folder-monitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mergepdf.folder-monitor.plist    # start
launchctl unload ~/Library/LaunchAgents/com.mergepdf.folder-monitor.plist  # stop
```

## Code Conventions

- Python 3.6+, snake_case, minimal docstrings
- Config values are hardcoded (no .env files)
- Shell scripts use bash with color output helpers
