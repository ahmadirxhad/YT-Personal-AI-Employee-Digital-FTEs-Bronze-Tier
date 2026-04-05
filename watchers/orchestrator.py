"""
orchestrator.py — Master process for the AI Employee Bronze Tier.

Responsibilities:
  1. Watch /Needs_Action for new .md files
  2. Trigger Claude Code to process them
  3. Watch /Approved for human-approved actions and execute them
  4. Update Dashboard.md with current status
  5. Manage audit logging

Usage:
  python orchestrator.py

Environment variables (set in .env):
  VAULT_PATH         — Path to AI_Employee_Vault directory
  CLAUDE_CMD         — Claude Code CLI command (default: claude)
  CHECK_INTERVAL     — Seconds between checks (default: 30)
  DRY_RUN            — Set to 'true' to log actions without executing (default: true)
"""
import os
import subprocess
import json
import time
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Orchestrator] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Orchestrator")

# ── Configuration ──────────────────────────────────────────────────────────────
VAULT_PATH = Path(os.getenv("VAULT_PATH", "../AI_Employee_Vault")).resolve()
CLAUDE_CMD = os.getenv("CLAUDE_CMD", "claude")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

NEEDS_ACTION = VAULT_PATH / "Needs_Action"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
DASHBOARD = VAULT_PATH / "Dashboard.md"
HANDBOOK = VAULT_PATH / "Company_Handbook.md"


# ── Helpers ────────────────────────────────────────────────────────────────────

def log_event(action_type: str, details: dict):
    """Append a structured log entry to today's JSON log."""
    log_file = LOGS / f"LOG_{datetime.now().strftime('%Y-%m-%d')}.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": "orchestrator",
        **details,
    }
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"Corrupt log file {log_file.name}, starting fresh: {e}")
            existing = []
    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def update_dashboard(status_updates: dict):
    """Update key lines in Dashboard.md."""
    if not DASHBOARD.exists():
        logger.warning("Dashboard.md not found, skipping update.")
        return

    content = DASHBOARD.read_text(encoding="utf-8")

    # Update timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = content.replace("{{TIMESTAMP}}", now)

    # Update folder counts
    for folder_name, folder_path in [
        ("/Inbox", VAULT_PATH / "Inbox"),
        ("/Needs_Action", NEEDS_ACTION),
        ("/Pending_Approval", VAULT_PATH / "Pending_Approval"),
    ]:
        count = len([f for f in folder_path.glob("*.md") if f.name != ".gitkeep"])
        content = content.replace(
            f"| {folder_name} | 0 |",
            f"| {folder_name} | {count} |",
        )

    DASHBOARD.write_text(content, encoding="utf-8")


def get_pending_files() -> list[Path]:
    """Return list of .md files in /Needs_Action not yet processed."""
    return [
        f for f in NEEDS_ACTION.glob("*.md")
        if f.name != ".gitkeep" and not f.name.startswith("_processed_")
    ]


def mark_processed(file_path: Path):
    """Move a processed file to /Done."""
    dest = DONE / file_path.name
    file_path.rename(dest)
    logger.info(f"Moved to /Done: {file_path.name}")


def trigger_claude(file_path: Path):
    """
    Call Claude Code CLI to process a Needs_Action file.
    Claude reads the file + Company_Handbook.md and creates a Plan.md.
    """
    prompt = f"""You are an AI Employee assistant. Read the following task file and the Company Handbook, then create a Plan.md file in the vault's /Plans folder.

Task file: {file_path}
Company Handbook: {HANDBOOK}
Vault path: {VAULT_PATH}

Instructions:
1. Read the task file carefully
2. Check Company_Handbook.md for relevant rules
3. Create a plan file at {VAULT_PATH}/Plans/PLAN_{file_path.stem}.md
4. If any action requires approval, create an approval file at {VAULT_PATH}/Pending_Approval/APPROVAL_{file_path.stem}.md
5. Update Dashboard.md with a brief note in Recent Activity
6. Do NOT take any external actions (no emails, no payments) without an approval file being moved to /Approved first

Follow the Company Handbook rules strictly.
"""
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would trigger Claude for: {file_path.name}")
        logger.info(f"[DRY RUN] Prompt preview:\n{prompt[:200]}...")
        return True

    try:
        logger.info(f"Triggering Claude for: {file_path.name}")
        result = subprocess.run(
            [CLAUDE_CMD, "--print", prompt],
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute timeout
        )
        if result.returncode == 0:
            logger.info(f"Claude completed task for: {file_path.name}")
            log_event("claude_triggered", {
                "file": file_path.name,
                "result": "success",
            })
            return True
        else:
            logger.error(f"Claude error: {result.stderr[:200]}")
            log_event("claude_triggered", {
                "file": file_path.name,
                "result": "error",
                "error": result.stderr[:200],
            })
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"Claude timed out processing: {file_path.name}")
        return False
    except FileNotFoundError:
        logger.error(f"Claude CLI not found. Is '{CLAUDE_CMD}' installed and in PATH?")
        return False


def process_approved_files():
    """
    Check /Approved for human-approved action files and execute them.
    Currently logs the approval — extend this to call MCP servers.
    """
    for approved_file in APPROVED.glob("*.md"):
        if approved_file.name == ".gitkeep":
            continue
        logger.info(f"Approved action detected: {approved_file.name}")
        log_event("action_approved", {
            "file": approved_file.name,
            "note": "Execution hook — connect MCP server here for Silver/Gold tier",
        })
        if not DRY_RUN:
            # Move to Done after execution
            dest = DONE / f"APPROVED_{approved_file.name}"
            approved_file.rename(dest)
        else:
            logger.info(f"[DRY RUN] Would execute action from: {approved_file.name}")


# ── Main Loop ──────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("AI Employee Orchestrator — Bronze Tier")
    logger.info(f"Vault: {VAULT_PATH}")
    logger.info(f"DRY RUN: {DRY_RUN}")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    logger.info("=" * 60)

    # Ensure all required vault folders exist
    for folder in [NEEDS_ACTION, APPROVED, DONE, LOGS,
                   VAULT_PATH / "Plans",
                   VAULT_PATH / "Pending_Approval",
                   VAULT_PATH / "Rejected"]:
        folder.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        logger.warning("DRY_RUN=true — no external actions will be taken.")
        logger.warning("Set DRY_RUN=false in .env when ready for live operation.")

    while True:
        try:
            # 1. Process new items in /Needs_Action
            pending = get_pending_files()
            if pending:
                logger.info(f"Found {len(pending)} item(s) in /Needs_Action")
                for file_path in pending:
                    success = trigger_claude(file_path)
                    if success:
                        mark_processed(file_path)

            # 2. Check /Approved for actions to execute
            process_approved_files()

            # 3. Update Dashboard
            update_dashboard({})

        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user.")
            break
        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)
            log_event("orchestrator_error", {"error": str(e)})

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
