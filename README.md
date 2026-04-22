# Salesforge Secret Sauce by RevSculpt

Create 50 multichannel sequences in Salesforge from your terminal. Email + LinkedIn, spintax, variables — all automated.

Created by [RevSculpt](https://revsculpt.com)

## What's Inside

```
├── salesforge-reference/SKILL.md      → Claude Code skill: API rules + traps
├── salesforge-sequence-creator/SKILL.md → Claude Code skill: paste copy → sequence
├── launcher.py                         → Create 50 sequences from campaign files
├── attach.py                           → Attach senders + enroll contacts to all sequences
└── examples/                           → Sample campaigns + contact CSV
```

## Quick Start

### 1. Install the Claude Code skills

```bash
git clone https://github.com/ajurkev/salesforge-secret-sauce-by-revsculpt.git
cd salesforge-secret-sauce-by-revsculpt
cp -r salesforge-reference salesforge-sequence-creator ~/.claude/skills/
```

### 2. Connect Salesforge MCP

Follow the [Salesforge MCP setup guide](https://help.salesforge.ai/en/articles/10333582-salesforge-mcp-server-connect-with-ai-assistants) to connect your Salesforge account to Claude Code.

### 3. Use interactively (one campaign at a time)

In Claude Code, type `/salesforge-sequence` and paste your email copy. It will:
- Generate spintax (3 variants per sentence)
- Check for spam words
- Convert to Salesforge format (`{{double_braces}}` variables)
- Push to Salesforge via MCP
- Sequence lands in **DRAFT** — you launch manually

### 4. Use the launcher (50 campaigns at once)

```bash
# Create your campaign files (see examples/ for format)
# Then run:
python3 launcher.py --key YOUR_SALESFORGE_API_KEY --workspace YOUR_WORKSPACE_ID

# After sequences are created, attach senders + enroll contacts:
python3 attach.py --key YOUR_SALESFORGE_API_KEY --workspace YOUR_WORKSPACE_ID --sender-profile-id YOUR_SENDER_ID
```

## Campaign File Format

Each `.txt` file in your campaigns folder defines a multichannel sequence:

```
--- STEP 1: EMAIL (Day 0) ---
Subject: {{first_name}}, compliance at {{company}}
Body: Your email body here with {{company}} variables.

--- STEP 2: EMAIL FOLLOW-UP (Day 3) ---
Subject: {{first_name}}, compliance at {{company}}
Body: Follow-up body here.

--- STEP 3: LINKEDIN VIEW PROFILE (Day 4) ---
(no message)

--- STEP 4: LINKEDIN CONNECTION REQUEST (Day 5) ---
Message: {{first_name}}, I work with companies like {{company}}...

--- STEP 5: LINKEDIN MESSAGE (Day 7) ---
Message: Thanks for connecting, {{first_name}}...

--- STEP 6: LINKEDIN FOLLOW-UP (Day 10) ---
Message: Last note on this, {{first_name}}...
```

## Key Traps (Already Solved)

1. **`metadata.message`** — email body is nested, not flat. Wrong field = blank emails, no error
2. **Integer IDs** — `actionId`, `branchId`, `senderProfileIds` are integers, not strings
3. **`{{double_braces}}`** — variables use `{{first_name}}`, NOT `{first_name}`
4. **Branch chaining** — each node creates a new branch. Re-fetch before adding next node
5. **`waitDays` vs `wait_in_minutes`** — create uses days, update uses minutes
6. **Schedule disabled days** — `from:0, to:0` → 422 error. Use `to:23`

## Variables

| Field | Format |
|---|---|
| First name | `{{first_name}}` |
| Last name | `{{last_name}}` |
| Company | `{{company}}` |
| Email | `{{email}}` |
| Job title | `{{job_title}}` |
| Custom | `{{your_custom_var}}` |

## Action IDs

| ID | Channel | Action |
|---|---|---|
| 1 | LinkedIn | Connection request |
| 2 | LinkedIn | Send message |
| 3 | Email | Send email |
| 4 | LinkedIn | View profile |
| 6 | LinkedIn | Like latest post |
| 7 | LinkedIn | Follow profile |
| 8 | LinkedIn | Send InMail |

## License

MIT

---

Built by [RevSculpt](https://revsculpt.com)
