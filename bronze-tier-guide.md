# Bronze Tier — Complete Usage Guide

> Your AI Employee: local-first, human-in-the-loop, powered by Claude Code.

---

## How It Works (Big Picture)

```
You drop a file  →  Watcher detects it  →  Orchestrator calls Claude Code
     →  Claude creates a Plan  →  You review & approve  →  Action executes
```

The vault (`AI_Employee_Vault/`) is the shared brain. Claude reads from it and writes to it. Obsidian is your GUI to see everything happening in real time.

---

## Step 1 — One-Time Setup

### 1.1 Install dependencies

```bash
# Python packages (watchers)
pip install -r requirements.txt

# Claude Code CLI (if not already installed)
npm install -g @anthropic/claude-code
```

Verify Claude Code is working:

```bash
claude --version
```

### 1.2 Create your .env file

```bash
cp .env.example .env
```

Open `.env` and set these values:

| Variable | What to set |
|----------|-------------|
| `VAULT_PATH` | Leave as `./AI_Employee_Vault` (default works) |
| `DRY_RUN` | `true` to test safely, `false` for live operation |
| `CHECK_INTERVAL` | How often the orchestrator polls (default: `30` seconds) |
| `CLAUDE_CMD` | Usually just `claude` |
| `DROP_FOLDER` | Set to `./AI_Employee_Vault/Inbox` (drop files directly in Obsidian) |

### 1.3 Open the Vault in Obsidian

1. Open Obsidian
2. Click **"Open folder as vault"**
3. Select the `AI_Employee_Vault/` folder
4. You will see `Dashboard.md` — this is your live command center

> The `Inbox/` folder already exists inside the vault — no need to create anything.

---

## Step 2 — Start the System

You need **two terminal windows** running at the same time.

### Terminal 1 — Start the Watcher

**Option A: Filesystem Watcher (simplest, no API needed)**

```bash
cd watchers
python filesystem_watcher.py
```

This watches `AI_Employee_Vault/Inbox/`. Drop files there directly inside Obsidian and the AI Employee wakes up.

**Option B: Gmail Watcher (requires Google Cloud setup)**

```bash
cd watchers
python gmail_watcher.py
```

First run will open a browser for Google OAuth. After that it runs silently.

> See Section 5 for Gmail API setup instructions.

### Terminal 2 — Start the Orchestrator

```bash
cd watchers
python orchestrator.py
```

You will see output like:

```
2026-04-04 10:00:00 [Orchestrator] INFO: AI Employee Orchestrator — Bronze Tier
2026-04-04 10:00:00 [Orchestrator] INFO: Vault: .../AI_Employee_Vault
2026-04-04 10:00:00 [Orchestrator] WARNING: DRY_RUN=true — no external actions will be taken.
```

Both processes run in the background. Leave both terminal windows open.

---

## Step 3 — Give Your AI Employee a Task

### Method A — Drop a file

Drag any file (`.txt`, `.pdf`, `.docx`) into `AI_Employee_Vault/Inbox/` directly in Obsidian (or copy it there via file explorer).

The filesystem watcher will:
1. Detect the file
2. Create a `.md` task card in `AI_Employee_Vault/Needs_Action/`

The orchestrator will:
3. Detect the new task card (within 30 seconds)
4. Call Claude Code with the task + Company Handbook
5. Claude creates a `Plan_*.md` in `AI_Employee_Vault/Plans/`
6. If approval needed: creates `APPROVAL_*.md` in `AI_Employee_Vault/Pending_Approval/`

### Method B — Manually create a task card

Create a file directly in `AI_Employee_Vault/Needs_Action/` with this format:

```markdown
---
source: manual
priority: HIGH
date: 2026-04-04
---

# Task: Write a follow-up email to John

John sent a proposal on Monday. Please draft a professional follow-up asking
for clarification on the pricing section.
```

Save it. The orchestrator picks it up on the next check cycle.

---

## Step 4 — Review and Approve

When Claude needs your input, it creates a file in `AI_Employee_Vault/Pending_Approval/`.

**In Obsidian:**

1. Click the `Pending_Approval/` folder
2. Open the approval file and read Claude's proposed action
3. **To approve**: Drag/move the file to `Approved/`
4. **To reject**: Drag/move the file to `Rejected/`

The orchestrator detects the move and executes (or cancels) the action.

---

## Step 5 — Watch the Dashboard

Open `AI_Employee_Vault/Dashboard.md` in Obsidian. It updates automatically showing:

- Folder counts (Inbox, Needs_Action, Pending_Approval)
- Recent activity
- System health

---

## Folder Reference

| Folder | Your role | Claude's role |
|--------|-----------|---------------|
| `Inbox/` | **Drop files here** — this is the drop folder | Reads and classifies |
| `Needs_Action/` | Create task cards manually | Processes every `.md` file found |
| `Plans/` | Read to see Claude's thinking | Writes plans here |
| `Pending_Approval/` | **Move to Approved or Rejected** | Writes approval requests |
| `Approved/` | Move files here to approve | Executes approved actions |
| `Rejected/` | Move files here to reject | Archives, takes no action |
| `Done/` | Read-only archive | Moves completed items here |
| `Logs/` | Audit trail | Writes `LOG_YYYY-MM-DD.json` daily |

---

## Key Commands — Quick Reference

```bash
# Install Python deps
pip install -r requirements.txt

# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Setup environment
cp .env.example .env

# Start filesystem watcher
cd watchers && python filesystem_watcher.py

# Start Gmail watcher
cd watchers && python gmail_watcher.py

# Start orchestrator (required — keep running)
cd watchers && python orchestrator.py

# Keep alive with PM2 (optional, prevents watcher dying overnight)
npm install -g pm2
pm2 start watchers/orchestrator.py --interpreter python3
pm2 start watchers/filesystem_watcher.py --interpreter python3
pm2 save && pm2 startup
```

---

## Section 5 — Gmail API Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "AI Employee")
3. Go to **APIs & Services → Enable APIs** → search "Gmail API" → Enable
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop App**
6. Download the JSON file and rename it `credentials.json`
7. Move `credentials.json` into the `watchers/` folder (scripts run from there):

```bash
mv ~/Downloads/credentials.json watchers/credentials.json
```

8. Run the Gmail watcher — a browser will open for you to log in once:

```bash
cd watchers
python gmail_watcher.py
```

After login, a `token.json` is saved and future runs are automatic.

---

## Section 6 — Going Live (Disabling DRY_RUN)

By default `DRY_RUN=true` — Claude plans everything but executes nothing externally.

When you are confident the system works correctly:

1. Open `.env`
2. Change `DRY_RUN=true` to `DRY_RUN=false`
3. Restart the orchestrator

```bash
# Stop with Ctrl+C, then restart
cd watchers && python orchestrator.py
```

---

## Section 7 — Editing the Rules

Claude reads `AI_Employee_Vault/Company_Handbook.md` before every action.

Edit this file to customize:
- Which actions need approval vs auto-approve
- Priority keywords (URGENT, HIGH, MEDIUM, LOW)
- Communication tone and style
- Financial thresholds
- Working hours

Changes take effect on the next task Claude processes — no restart needed.

---

## Section 8 — Troubleshooting

| Problem | Fix |
|---------|-----|
| `claude: command not found` | Run `npm install -g @anthropic/claude-code` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Gmail 403 Forbidden | Enable Gmail API in Google Cloud Console |
| Watcher stops overnight | Use PM2 (see Key Commands above) |
| Tasks not processing | Check orchestrator is running in Terminal 2 |
| DRY RUN in logs | Set `DRY_RUN=false` in `.env` when ready |

---

## Section 9 — Agent Skills

The AI Employee uses these built-in skills (in `.agents/skills/`):

| Skill | What it does |
|-------|-------------|
| `vault-manager` | Reads and writes vault files, moves items between folders |
| `task-processor` | Classifies tasks and creates plans |
| `dashboard-updater` | Refreshes `Dashboard.md` with live counts |
| `file-watcher` | Filesystem monitoring logic |
| `gws-gmail-watch` | Gmail API integration |
| `cron-scheduling` | Scheduled triggers |

You do not call these directly — the orchestrator and Claude use them automatically.

---

## Section 10 — Daily Workflow

**Morning check-in (5 minutes):**

1. Open Obsidian → `Dashboard.md`
2. Check `Pending_Approval/` for items needing your decision
3. Move files to `Approved/` or `Rejected/`
4. Glance at `Logs/` for yesterday's activity

**To give Claude a new task:**

- Drop a file into `AI_Employee_Vault/Inbox/` in Obsidian, or
- Create a `.md` file in `Needs_Action/` manually

That's it. Claude does the rest.

---

*Bronze Tier v0.1 · Powered by Claude Code · Part of Personal AI Employee Hackathon 0*
