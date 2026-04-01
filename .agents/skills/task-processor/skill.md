# Task Processor Skill

Processes items from the AI Employee vault's `/Needs_Action` folder.
Use this skill to analyze incoming tasks, create plans, and route items
to the correct folder based on Company_Handbook.md rules.

## When to Use This Skill

- When the orchestrator triggers you with a Needs_Action file path
- When the user asks you to "process inbox" or "check Needs_Action"
- When you need to classify and route incoming items

## Processing Workflow

### Step 1: Read the task file
Read the file from `/Needs_Action/` and extract:
- `type` (email, file_drop, manual)
- `priority` (URGENT, HIGH, MEDIUM, LOW)
- `status`
- The content/description

### Step 2: Read Company_Handbook.md
Always check the handbook before deciding what to do.
Key sections to check:
- Section 3: Financial Rules (for payment-related items)
- Section 4: Approval Thresholds
- Section 5: Priority Levels
- Section 10: Escalation Protocol

### Step 3: Create a Plan
Create a plan file at `Plans/PLAN_<task_slug>.md`:

```markdown
---
created: <ISO timestamp>
task_file: <source file name>
status: in_progress
---

## Objective
<One sentence: what needs to be accomplished>

## Steps
- [x] Read task file
- [x] Check Company_Handbook.md
- [ ] <next step>
- [ ] <next step>

## Decision
<Why you chose this approach>

## Approval Required?
<Yes/No — if yes, describe what needs approval>
```

### Step 4: Route the item

**If action is safe to log only (no external action):**
- Update the task file status to `processed`
- Move to `/Done`
- Update Dashboard.md

**If action requires human approval:**
- Create approval file in `/Pending_Approval/`
- Update task file status to `awaiting_approval`
- Update Dashboard.md Pending Approvals section

**If item is unclear or escalation needed:**
- Update task file: add `status: needs_human_review`
- Leave in `/Needs_Action` (do NOT move)
- Add a comment explaining what is unclear

### Step 5: Update Dashboard.md
After processing, add to Recent Activity:
```
- [<YYYY-MM-DD HH:MM>] <type>: <brief description> → <outcome>
```

## Priority Handling

| Priority | Response |
|----------|----------|
| URGENT | Process immediately, flag in Dashboard |
| HIGH | Process in current cycle |
| MEDIUM | Process in current cycle |
| LOW | Can batch with other LOW items |

## Email Processing Rules
1. Extract: sender, subject, snippet
2. Check if sender is a known contact (search Done/ and Logs/ for prior emails)
3. Draft a reply plan — always put in Pending_Approval, never auto-send
4. Log the email in today's LOG file

## File Drop Processing Rules
1. Read the metadata file
2. Classify: invoice / contract / report / image / other
3. Create a plan for what to do with it
4. If it looks like a financial document → HIGH priority + approval required

## Output Format
After processing, respond with:
```
PROCESSED: <filename>
Plan: Plans/PLAN_<slug>.md
Outcome: <moved_to_done | awaiting_approval | needs_human_review>
Notes: <brief note>
```
