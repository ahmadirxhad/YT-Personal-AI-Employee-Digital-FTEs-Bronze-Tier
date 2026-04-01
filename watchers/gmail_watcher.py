"""
gmail_watcher.py — Watches Gmail for important unread emails and creates
action files in the Obsidian vault's /Needs_Action folder.

Setup:
  1. Enable Gmail API: https://developers.google.com/gmail/api/quickstart/python
  2. Download credentials.json to this directory
  3. Run once interactively to generate token.json
  4. Set VAULT_PATH in .env
"""
import os
import pickle
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base_watcher import BaseWatcher

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Keywords that raise priority to URGENT
URGENT_KEYWORDS = ["urgent", "asap", "emergency", "payment failed", "account suspended"]
# Keywords that raise priority to HIGH
HIGH_KEYWORDS = ["invoice", "payment", "proposal", "contract", "deadline"]


def _get_priority(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in URGENT_KEYWORDS):
        return "URGENT"
    if any(kw in text_lower for kw in HIGH_KEYWORDS):
        return "HIGH"
    return "MEDIUM"


class GmailWatcher(BaseWatcher):
    """Watches Gmail for important unread emails."""

    def __init__(self, vault_path: str, credentials_path: str = "credentials.json"):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        self.credentials_path = Path(credentials_path)
        self.token_path = Path("token.json")
        self.processed_ids: set = set()
        self.service = self._authenticate()

    def _authenticate(self):
        """Handle OAuth2 authentication for Gmail API."""
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}. "
                        "Download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            self.token_path.write_text(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def check_for_updates(self) -> list:
        """Return list of unread important messages not yet processed."""
        try:
            results = self.service.users().messages().list(
                userId="me", q="is:unread is:important"
            ).execute()
            messages = results.get("messages", [])
            return [m for m in messages if m["id"] not in self.processed_ids]
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []

    def create_action_file(self, message: dict) -> Path:
        """Fetch email details and create a .md action file."""
        try:
            msg = self.service.users().messages().get(
                userId="me", id=message["id"], format="full"
            ).execute()

            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            subject = headers.get("Subject", "No Subject")
            sender = headers.get("From", "Unknown")
            snippet = msg.get("snippet", "")
            priority = _get_priority(f"{subject} {snippet}")

            content = f"""---
type: email
message_id: {message["id"]}
from: "{sender}"
subject: "{subject}"
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

## Email Summary
**From:** {sender}
**Subject:** {subject}
**Received:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Priority:** {priority}

## Snippet
{snippet}

## Suggested Actions
- [ ] Review email content
- [ ] Draft reply (place in /Pending_Approval if sending)
- [ ] Archive after processing

## Notes
_Add your notes here_
"""
            filepath = self.needs_action / f"EMAIL_{message['id']}.md"
            filepath.write_text(content, encoding="utf-8")
            self.processed_ids.add(message["id"])
            self.logger.info(f"[{priority}] New email: {subject[:60]}")
            return filepath

        except HttpError as e:
            self.logger.error(f"Failed to fetch message {message['id']}: {e}")
            return None


if __name__ == "__main__":
    vault_path = os.getenv("VAULT_PATH", "../AI_Employee_Vault")
    creds_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")

    watcher = GmailWatcher(vault_path=vault_path, credentials_path=creds_path)
    watcher.run()
