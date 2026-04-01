"""
filesystem_watcher.py — Watches a "drop folder" for new files and creates
action files in the Obsidian vault's /Needs_Action folder.

This is the simplest watcher — drag any file into the DROP_FOLDER and
the AI Employee will pick it up and create a task.

Setup:
  1. Set DROP_FOLDER in .env (default: ~/Desktop/AI_Drop)
  2. Set VAULT_PATH in .env
  3. Run: python filesystem_watcher.py
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from base_watcher import BaseWatcher

load_dotenv()

# File extensions to ignore
IGNORED_EXTENSIONS = {".tmp", ".part", ".crdownload", ".gitkeep"}


class DropFolderHandler(FileSystemEventHandler):
    """watchdog event handler — fires when a new file lands in the drop folder."""

    def __init__(self, needs_action: Path, logs_dir: Path, logger):
        self.needs_action = needs_action
        self.logs_dir = logs_dir
        self.logger = logger

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        if source.suffix.lower() in IGNORED_EXTENSIONS:
            return

        # Small delay to ensure file is fully written
        import time
        time.sleep(0.5)

        try:
            dest = self.needs_action / f"FILE_{source.name}"
            shutil.copy2(source, dest)
            self._create_metadata(source)
            self.logger.info(f"Picked up file: {source.name}")
        except Exception as e:
            self.logger.error(f"Failed to process {source.name}: {e}")

    def _create_metadata(self, source: Path):
        """Create a companion .md metadata file in /Needs_Action."""
        stat = source.stat()
        size_kb = stat.st_size / 1024

        content = f"""---
type: file_drop
original_name: "{source.name}"
original_path: "{source}"
size_bytes: {stat.st_size}
size_kb: {size_kb:.1f}
dropped_at: {datetime.now().isoformat()}
priority: MEDIUM
status: pending
---

## File Dropped for Processing

**File:** `{source.name}`
**Size:** {size_kb:.1f} KB
**Dropped:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## What to do
- [ ] Review the file content
- [ ] Classify: invoice / contract / report / other
- [ ] Take appropriate action per Company_Handbook.md

## Notes
_Add your notes here_
"""
        meta_path = self.needs_action / f"FILE_{source.stem}_meta.md"
        meta_path.write_text(content, encoding="utf-8")


class FilesystemWatcher(BaseWatcher):
    """Watches a drop folder for new files using watchdog."""

    def __init__(self, vault_path: str, drop_folder: str):
        super().__init__(vault_path, check_interval=5)
        self.drop_folder = Path(drop_folder)
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Drop folder: {self.drop_folder}")

    def check_for_updates(self) -> list:
        # Not used — watchdog handles events via DropFolderHandler
        return []

    def create_action_file(self, item) -> Path:
        # Not used — DropFolderHandler handles file creation
        return None

    def run(self):
        """Start watchdog observer on the drop folder."""
        self.logger.info(f"Watching drop folder: {self.drop_folder}")
        handler = DropFolderHandler(self.needs_action, self.logs_dir, self.logger)
        observer = Observer()
        observer.schedule(handler, str(self.drop_folder), recursive=False)
        observer.start()
        self.logger.info("Filesystem watcher running. Drop files to trigger AI Employee.")

        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info("Filesystem watcher stopped.")
        observer.join()


if __name__ == "__main__":
    vault_path = os.getenv("VAULT_PATH", "../AI_Employee_Vault")
    drop_folder = os.getenv("DROP_FOLDER", str(Path.home() / "Desktop" / "AI_Drop"))

    watcher = FilesystemWatcher(vault_path=vault_path, drop_folder=drop_folder)
    watcher.run()
