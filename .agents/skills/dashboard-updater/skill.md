# Dashboard Updater Skill

Updates the AI Employee's `Dashboard.md` with current vault status.
Use this skill after any significant action, or when asked to "refresh dashboard"
or "update status".

## When to Use

- After processing items from /Needs_Action
- After an approval is granted or rejected
- After watcher scripts detect new items
- On a scheduled basis (e.g., every 30 minutes)
- When user asks: "what's the status?" or "update dashboard"

## Dashboard Sections to Update

### 1. Header timestamp
Replace `{{TIMESTAMP}}` or the existing timestamp with current datetime.

### 2. System Status table
Check each watcher by looking for recent log entries in `Logs/`:
- If LOG file has entries in last 5 minutes → 🟢 Running
- If LOG file has entries in last hour → 🟡 Idle
- If no recent LOG entries → 🔴 Stopped

### 3. Inbox Summary table
Count .md files (excluding .gitkeep) in each folder:
```
Inbox → count
Needs_Action → count
Pending_Approval → count
Done (today) → count files modified today
```

### 4. Recent Activity
Keep the 10 most recent entries. Format:
```
- [YYYY-MM-DD HH:MM] <action type>: <brief description>
```
Read from today's LOG file to get recent actions.

### 5. Active Tasks
List items currently in /Needs_Action with their priority and status.
Format:
```
- [PRIORITY] filename.md — status
```

### 6. Pending Approvals
List all files in /Pending_Approval with creation time.
Format:
```
- APPROVAL_filename.md (created: YYYY-MM-DD)
```

### 7. Quick Stats (This Week)
Read all LOG files from the past 7 days and count:
- `action_file_created` entries → "Emails/Files processed"
- `action_approved` entries → "Actions approved"
- `claude_triggered` entries → "Actions taken"

## Update Procedure

1. Read current `Dashboard.md`
2. Compute all new values (counts, timestamps, log summaries)
3. Write the updated Dashboard.md
4. Log the dashboard update to today's LOG file

## Example Updated Dashboard Snippet

```markdown
## Inbox Summary

| Folder | Count |
|--------|-------|
| /Inbox | 2 |
| /Needs_Action | 1 |
| /Pending_Approval | 3 |
| /Done (today) | 5 |

## Recent Activity
- [2026-04-01 09:15] email: Invoice request from Client A → awaiting_approval
- [2026-04-01 08:45] file_drop: Q1_Report.pdf → moved_to_done
- [2026-04-01 08:00] Dashboard updated
```

## Notes
- Never delete existing history — only prepend new entries
- If a section is missing from Dashboard.md, append it at the end
- Keep the file clean and human-readable — this is the owner's primary UI
