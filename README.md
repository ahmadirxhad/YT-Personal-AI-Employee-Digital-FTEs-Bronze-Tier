# Personal AI Employee — Bronze Tier

> **Hackathon:** Personal AI Employee Hackathon 0 — Building Autonomous FTEs in 2026
> **Tier:** 🥉 Bronze (Foundation — Minimum Viable Deliverable)
> **Engine:** Claude Code + Obsidian (local-first)

---

## What This Is

A local-first AI Employee that monitors your Gmail and filesystem, creates
structured tasks in an Obsidian vault, and uses Claude Code to reason about
and plan responses — all with human-in-the-loop approval for sensitive actions.

---

## Architecture

```
┌─────────────────────────────────────────┐
│         EXTERNAL SOURCES                │
│   Gmail API        Drop Folder          │
└────────┬─────────────────┬──────────────┘
         ▼                 ▼
┌─────────────────────────────────────────┐
│         PERCEPTION LAYER (Watchers)     │
│   gmail_watcher.py  filesystem_watcher  │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│         OBSIDIAN VAULT (Local)          │
│  /Inbox  /Needs_Action  /Plans  /Done   │
│  Dashboard.md   Company_Handbook.md     │
│  /Pending_Approval  /Approved           │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│         REASONING LAYER                 │
│   orchestrator.py → Claude Code CLI     │
│   Agent Skills: vault-manager,          │
│   task-processor, dashboard-updater     │
└────────────────────┬────────────────────┘
                     ▼
┌─────────────────────────────────────────┐
│         HUMAN-IN-THE-LOOP               │
│   Review /Pending_Approval files        │
│   Move to /Approved or /Rejected        │
└─────────────────────────────────────────┘
```

---

## Bronze Tier Checklist

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (Gmail + Filesystem)
- [x] Claude Code reads from and writes to the vault via orchestrator
- [x] Folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] All AI functionality implemented as Agent Skills

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Latest | AI reasoning engine |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Obsidian](https://obsidian.md) | 1.10.6+ | Vault GUI |
| [Node.js](https://nodejs.org) | v24+ | Skills CLI |

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo>
cd YT-Personal-AI-Employee-Digital-FTEs-Bronze-Tier

# Install Python dependencies
pip install -r requirements.txt
# or with uv:
# uv pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Open the vault in Obsidian

1. Open Obsidian → "Open folder as vault"
2. Select the `AI_Employee_Vault/` folder
3. You'll see `Dashboard.md` open automatically

### 4. Set up Gmail API (for Gmail Watcher)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable Gmail API
3. Create OAuth 2.0 credentials → Download `credentials.json`
4. Place `credentials.json` in the `watchers/` folder
5. First run will open a browser for OAuth consent

### 5. Start the watchers

**Option A — Gmail Watcher:**
```bash
cd watchers
python gmail_watcher.py
```

**Option B — Filesystem Watcher (simpler, no API needed):**
```bash
cd watchers
python filesystem_watcher.py
# Then drag files into ~/Desktop/AI_Drop to trigger the AI
```

### 6. Start the Orchestrator

```bash
cd watchers
python orchestrator.py
```

> By default `DRY_RUN=true` — nothing will be executed externally.
> Set `DRY_RUN=false` in `.env` when ready for live operation.

---

## How It Works

1. **Watcher** detects a new email or dropped file
2. **Watcher** creates a `.md` action file in `/Needs_Action`
3. **Orchestrator** detects the new file and calls Claude Code
4. **Claude Code** reads the task + `Company_Handbook.md` and creates a `Plan.md`
5. If the action is safe: Claude moves the item to `/Done`
6. If approval is needed: Claude creates a file in `/Pending_Approval`
7. **You** review the approval file and move it to `/Approved` or `/Rejected`
8. **Orchestrator** detects the approval and executes the action
9. **Dashboard.md** is updated throughout

---

## Agent Skills

| Skill | Purpose |
|-------|---------|
| `vault-manager` | Read/write vault files, move items between folders |
| `task-processor` | Classify and plan responses to Needs_Action items |
| `dashboard-updater` | Refresh Dashboard.md with current vault status |
| `gws-gmail-watch` | Gmail API integration guidance |
| `file-watcher` | Filesystem monitoring patterns |
| `cron-scheduling` | Schedule watcher triggers |
| `browsing-with-playwright` | Web automation (WhatsApp — Silver Tier) |

---

## Security

- **Credentials**: Stored in `.env` (gitignored), never in vault markdown
- **DRY_RUN**: All external actions disabled by default
- **HITL**: Every external action requires file-based human approval
- **Audit log**: Every action logged to `AI_Employee_Vault/Logs/LOG_YYYY-MM-DD.json`
- **No auto-payments**: Financial actions always require explicit approval

---

## File Structure

```
├── AI_Employee_Vault/           # Obsidian vault (open this in Obsidian)
│   ├── Dashboard.md             # Live status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # KPIs and objectives
│   ├── Inbox/                   # Raw unclassified items
│   ├── Needs_Action/            # Items for Claude to process
│   ├── Plans/                   # Plans Claude has created
│   ├── Pending_Approval/        # Awaiting your approval
│   ├── Approved/                # Approved, ready to execute
│   ├── Rejected/                # Rejected actions (archived)
│   ├── Done/                    # Completed items
│   └── Logs/                    # JSON audit logs
├── watchers/
│   ├── base_watcher.py          # Abstract base class
│   ├── gmail_watcher.py         # Gmail API watcher
│   ├── filesystem_watcher.py    # Drop-folder watcher
│   └── orchestrator.py          # Master process
├── .agents/skills/              # Agent Skills
│   ├── vault-manager/           # Vault R/W operations
│   ├── task-processor/          # Task classification & planning
│   ├── dashboard-updater/       # Dashboard refresh
│   ├── gws-gmail-watch/         # Gmail integration
│   ├── file-watcher/            # Filesystem monitoring
│   ├── cron-scheduling/         # Scheduling
│   └── browsing-with-playwright/ # Web automation
├── requirements.txt
├── .env.example                 # Copy to .env and fill in values
└── README.md
```

---

## Troubleshooting

**Claude CLI not found:**
```bash
npm install -g @anthropic/claude-code
```

**Gmail 403 Forbidden:**
Check that Gmail API is enabled in Google Cloud Console and OAuth consent is configured.

**Watcher stops overnight:**
Use PM2 to keep it alive:
```bash
npm install -g pm2
pm2 start watchers/gmail_watcher.py --interpreter python3
pm2 save && pm2 startup
```

---

## Next Steps (Silver Tier)

- Add WhatsApp Watcher via Playwright
- Add Email MCP server for sending replies
- Add LinkedIn auto-posting
- Add Human-in-the-Loop scheduling via cron

---

*Built for Personal AI Employee Hackathon 0 · Powered by Claude Code*
