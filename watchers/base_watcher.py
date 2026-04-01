"""
base_watcher.py — Abstract base class for all AI Employee watchers.
All watchers inherit from this class to ensure consistent behavior.
"""
import time
import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class BaseWatcher(ABC):
    """Base class for all AI Employee watchers."""

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / "Inbox"
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_dir = self.vault_path / "Logs"
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self._ensure_folders()

    def _ensure_folders(self):
        """Create required vault folders if they don't exist."""
        for folder in [self.inbox, self.needs_action, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process."""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create a .md file in Needs_Action folder and return its path."""
        pass

    def log_action(self, action_type: str, details: dict):
        """Write a structured log entry to the daily log file."""
        log_file = self.logs_dir / f"LOG_{datetime.now().strftime('%Y-%m-%d')}.json"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": self.__class__.__name__,
            **details,
        }
        # Append to today's log
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        existing.append(entry)
        log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    def run(self):
        """Main loop — polls for updates and creates action files."""
        self.logger.info(f"Starting {self.__class__.__name__} (interval: {self.check_interval}s)")
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    path = self.create_action_file(item)
                    if path:
                        self.logger.info(f"Created action file: {path.name}")
                        self.log_action("action_file_created", {"file": str(path.name)})
            except KeyboardInterrupt:
                self.logger.info(f"Stopping {self.__class__.__name__}")
                break
            except Exception as e:
                self.logger.error(f"Error during check: {e}", exc_info=True)
            time.sleep(self.check_interval)
