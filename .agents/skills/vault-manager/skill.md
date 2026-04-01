# Vault Manager Skill

Manages read/write operations on the AI Employee Obsidian vault.
Use this skill whenever you need to interact with the vault's folder structure,
create action files, move items between folders, or query vault state.

## Vault Structure

```
AI_Employee_Vault/
├── Inbox/              — Raw items not yet classified
├── Needs_Action/       — Items requiring AI processing
├── Plans/              — Plans Claude has created
├── Pending_Approval/   — Actions waiting for human approval
├── Approved/           — Human-approved, ready to execute
├── Rejected/           — Human-rejected (archived)
├── Done/               — Completed items
├── Logs/               — Audit trail (JSON per day)
├── Dashboard.md        — Live status dashboard
├── Company_Handbook.md — Rules of engagement
└── Business_Goals.md   — Goals and KPIs
```

## Core Operations

### Read vault status
Count files in each folder and report totals.
```
Read all .md files from each folder (exclude .gitkeep)
Report: { folder: count } for Inbox, Needs_Action, Pending_Approval, Done
```

### Create action file
When a watcher detects something (email, file drop, etc.):
```markdown
---
type: <email|file_drop|manual>
source: <description>
received: <ISO timestamp>
priority: <URGENT|HIGH|MEDIUM|LOW>
status: pending
---

## Summary
<one-line description of what this item is>

## Details
<relevant details>

## Suggested Actions
- [ ] <action 1>
- [ ] <action 2>
```
Save to: `Needs_Action/<TYPE>_<id>.md`

### Move item to Done
After an item is fully processed:
1. Read the file from its current location
2. Write it to `Done/<original_filename>`
3. Delete the original

### Create approval request
When an action requires human approval:
```markdown
---
type: approval_request
action: <action_type>
created: <ISO timestamp>
expires: <ISO timestamp, 24h later>
status: pending
---

## Action Requested
<clear description of what will happen>

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```
Save to: `Pending_Approval/APPROVAL_<action>_<date>.md`

### Update Dashboard.md
After every significant action, update Dashboard.md:
1. Update the "Last Updated" timestamp
2. Refresh folder counts in the Inbox Summary table
3. Append to Recent Activity (keep last 10 entries)
4. Update Pending Approvals list

## Rules (from Company_Handbook.md)
- Always read Company_Handbook.md before taking action
- Never delete files — move to /Done or /Rejected instead
- Never store credentials in vault files
- Log every action to Logs/LOG_YYYY-MM-DD.json
- When uncertain: create a Needs_Action file instead of acting

## File Naming
```
EMAIL_<message_id>.md
FILE_<original_name>_meta.md
PLAN_<task_slug>.md
APPROVAL_<action>_<YYYY-MM-DD>.md
LOG_<YYYY-MM-DD>.json
```
