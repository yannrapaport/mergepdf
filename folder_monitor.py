import argparse
import logging
import os
import shutil
import time
from datetime import datetime

from PyPDF2 import PdfReader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mergepdf import merge_pdfs

DEFAULT_WATCH_DIR = os.path.expanduser("~/Downloads")
PAIRING_TIMEOUT_SECONDS = 180
PAGE_COUNT_TOLERANCE = 1

logger = logging.getLogger("folder_monitor")


def get_page_count(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        logger.warning("Could not read %s: %s", pdf_path, e)
        return None


def wait_for_stable(path, interval=0.5, checks=3):
    prev_size = -1
    stable_count = 0
    while stable_count < checks:
        try:
            size = os.path.getsize(path)
        except OSError:
            return False
        if size == prev_size:
            stable_count += 1
        else:
            stable_count = 0
            prev_size = size
        time.sleep(interval)
    return True


class PdfPairingBuffer:
    def __init__(self, output_dir, watch_dir):
        self.pending = None  # (path, page_count, arrival_time)
        self.output_dir = output_dir
        self.watch_dir = watch_dir
        self.processed_dir = os.path.join(watch_dir, "processed")

    def on_new_pdf(self, path):
        if not wait_for_stable(path):
            logger.warning("File disappeared before it could be read: %s", path)
            return

        page_count = get_page_count(path)
        if page_count is None:
            return

        logger.info("New PDF: %s (%d pages)", os.path.basename(path), page_count)

        if self.pending is None:
            self.pending = (path, page_count, time.time())
            logger.info("Waiting for a matching second PDF...")
            return

        pending_path, pending_count, _ = self.pending

        if abs(pending_count - page_count) <= PAGE_COUNT_TOLERANCE:
            self._merge_pair(pending_path, path)
            self.pending = None
        else:
            logger.warning(
                "Page count mismatch: %s (%d pages) vs %s (%d pages). "
                "Dropping %s from pairing buffer.",
                os.path.basename(pending_path), pending_count,
                os.path.basename(path), page_count,
                os.path.basename(pending_path),
            )
            self.pending = (path, page_count, time.time())

    def _merge_pair(self, odd_path, even_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"merged_{timestamp}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)

        logger.info(
            "Merging: %s (odd) + %s (even) -> %s",
            os.path.basename(odd_path),
            os.path.basename(even_path),
            output_filename,
        )

        try:
            merge_pdfs(odd_path, even_path, output_path)
        except Exception as e:
            logger.error("Merge failed: %s", e)
            return

        os.makedirs(self.processed_dir, exist_ok=True)
        for src in (odd_path, even_path):
            dest = os.path.join(self.processed_dir, os.path.basename(src))
            # Avoid overwriting an existing file in processed/
            if os.path.exists(dest):
                name, ext = os.path.splitext(os.path.basename(src))
                dest = os.path.join(self.processed_dir, f"{name}_{timestamp}{ext}")
            shutil.move(src, dest)
            logger.info("Moved %s -> processed/", os.path.basename(src))

        logger.info("Merge complete: %s", output_path)

    def check_timeout(self):
        if self.pending is None:
            return
        _, _, arrival_time = self.pending
        if time.time() - arrival_time > PAIRING_TIMEOUT_SECONDS:
            path = self.pending[0]
            logger.warning(
                "Timeout: no matching PDF arrived for %s. Clearing buffer.",
                os.path.basename(path),
            )
            self.pending = None


class PdfEventHandler(FileSystemEventHandler):
    def __init__(self, pairing_buffer):
        super().__init__()
        self.buffer = pairing_buffer

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.lower().endswith(".pdf"):
            return
        # Ignore files in the processed subfolder
        if os.path.sep + "processed" + os.path.sep in event.src_path:
            return
        # Ignore merged output files
        if os.path.basename(event.src_path).startswith("merged_"):
            return
        self.buffer.on_new_pdf(event.src_path)


def run_monitor(watch_dir, output_dir, timeout):
    global PAIRING_TIMEOUT_SECONDS
    PAIRING_TIMEOUT_SECONDS = timeout

    watch_dir = os.path.abspath(os.path.expanduser(watch_dir))
    output_dir = os.path.abspath(os.path.expanduser(output_dir))

    if not os.path.isdir(watch_dir):
        logger.error("Watch directory does not exist: %s", watch_dir)
        return

    os.makedirs(output_dir, exist_ok=True)

    buffer = PdfPairingBuffer(output_dir, watch_dir)
    handler = PdfEventHandler(buffer)

    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()

    logger.info("Monitoring %s for new PDFs (timeout: %ds)", watch_dir, timeout)

    try:
        while True:
            buffer.check_timeout()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
    finally:
        observer.stop()
        observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="Monitor a folder for scanned PDFs and automatically merge odd/even pairs."
    )
    parser.add_argument(
        "-w", "--watch-dir",
        default=DEFAULT_WATCH_DIR,
        help="Folder to monitor (default: ~/Downloads)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output folder for merged PDFs (default: same as watch dir)",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=PAIRING_TIMEOUT_SECONDS,
        help="Seconds to wait for a matching PDF (default: 180)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    output_dir = args.output_dir if args.output_dir else args.watch_dir
    run_monitor(args.watch_dir, output_dir, args.timeout)


if __name__ == "__main__":
    main()
