---
name: salesforge-sequence
description: Create Salesforge email sequences end-to-end — spam check, spam fix, spintax, variable mapping, and sequence deployment. Works standalone (paste any copy) or reads from a campaign file. Use after copywriting is complete or whenever you need to push copy to Salesforge. Sequence is created PAUSED — launch is always manual.
---

# Salesforge Sequence Creator — Push-Button Pipeline

Paste copy → live Salesforge sequence (paused, ready for manual launch).

> **Before proceeding:** Invoke the `salesforge` reference skill now to load all API rules (sequence constraints, variable handling, pagination, defaults, error handling). Do not skip this.

---

## Mode Detection

### Standalone Mode (PRIMARY)

If user provides a file path or pastes copy directly:
1. If a file path is given, read it with the Read tool
2. Parse by looking for: "Email 1", "Email 2", "Subject:", "Body:", numbered headers, "---" separators
3. If structure is ambiguous, show what was parsed and ask user to confirm
4. Ask: "Which workspace is this for?" — needed for Salesforge context

### Pipeline Mode (SECONDARY)

If a campaign copywriting file exists in context:
1. Read the copywriting file for email sequences
2. Read any campaign strategy file for tiers, variables, routing logic
3. Read client overview for context

**Both modes continue to Step 1 below.**

---

## The 8-Step Pipeline

### Step 1 — Parse Emails

Extract from the copy source:
- Sequence name / campaign tier
- Email position (Email 1, 2, 3, 4)
- Thread structure (new thread vs reply)
- Subject line (new-thread emails only)
- Body text
- All variables used

**Thread structure:**

| Email | is_reply | wait_days | Subject |
|-------|----------|-----------|---------|
| 1 | false | 1 | Required (new thread) |
| 2 | true | 2-3 | Same as Email 1 subject (reply) |
| 3 | false | 3-4 | Required (new thread) |
| 4 | true | 2-3 | Same as Email 3 subject (reply) |

**Labeled email variants (e.g., Email 1a / 1b / 1c):**
STOP immediately. List every variant found and ask the user which variant goes in which step. Do NOT guess or merge.

---

### Step 2 — Apply Spintax

Invoke the `spintax-creator` skill on each email's copy.

**Required output format — 4 options per line:**
```
{original sentence | variation 1 | variation 2 | variation 3}
```

The ORIGINAL sentence must appear as option 1. Exactly 4 options total.

**Scope — apply to ALL emails:**
- Every body paragraph → its own 4-option spintax block
- Subject lines on new-thread emails (1 & 3) → spintaxed
- Thread-reply subjects → NOT spintaxed
- Do NOT spin: lines of 3 words or fewer, greeting lines (just salutation + name), variable-only lines, specific data/percentages, P.S. lines with metrics

**Spintax format:** `{opt1 | opt2 | opt3}` — single curly braces, pipe-separated. If Salesforge uses a different format, convert at Step 5.

---

### Step 3 — Spam Check

Run the `email-spam-fixer` skill on the spintaxed copy.

Treat any `{...}` block containing a `|` as spintax — check ALL variants inside it. Blocks without a `|` are variables — skip them.

---

### Step 4 — Fix Spam Words

The `email-spam-fixer` skill handles all fixes via Cyrillic lookalike characters.

**Post-fix variable integrity check (required):**
After running fix_spam.py, scan output for variable tokens. If any character inside a variable name was replaced with a Cyrillic lookalike, restore it to ASCII. Corrupted variable names break personalization silently.

---

### Step 5 — Convert Variables to Salesforge Format

⚠️ Variable format depends on Salesforge's actual implementation. Default mapping:

| Source variable | Salesforge format |
|---|---|
| `{{firstName}}` / `{{first_name}}` | `{first_name}` ⚠️ |
| `{{companyName}}` / `{{company_name}}` | `{company}` ⚠️ |
| `{{job_title}}` / `{{jobTitle}}` | `{job_title}` ⚠️ |
| `{{lastName}}` / `{{last_name}}` | `{last_name}` ⚠️ |

**Custom variables:** Map directly — `{{pain_point}}` → `{pain_point}`

Flag which variables need Clay enrichment vs. standard Salesforge contact fields.

⚠️ **First-run task:** Test variable rendering in Salesforge with a test sequence. Update the salesforge reference skill with confirmed format.

---

### Step 6 — Convert Bodies to HTML

Salesforge email bodies expect HTML. Convert plain text:

- Each paragraph → `<p>...</p>`
- Blank lines between paragraphs → `<p><br></p>`
- Single line breaks within paragraph → `<br>`
- No styling, no inline CSS, no classes
- Variables stay inline: `<p>Hi {first_name},</p>`
- Spintax stays inline

---

### Step 7 — Validate Spintax

Before approval gate, validate final HTML of every email:

1. **Balanced braces:** Count of `{` equals `}`
2. **Spintax completeness:** Every `{...}` with `|` has ≥ 2 non-empty options
3. **Variable format:** Every `{...}` without `|` matches expected variable pattern

**On failure:** Show broken token, attempt auto-repair, re-validate. If still broken, flag to user.

---

### Step 8 — Approval Gate

**STOP. Do not push to Salesforge until user approves.**

Display summary:

**Spam Fix Summary**
| Email | Flagged Words | Words Fixed | Status |
|-------|--------------|-------------|--------|
| Email 1 Subject | [list] | N | ✓ Clean / Fixed |
| Email 1 Body | [list] | N | ✓ Fixed |
| ... | | | |

**Sequence Overview**
| Step | is_reply | wait_days | Subject | Body Lines | Spintaxed? |
|------|----------|-----------|---------|-----------|-----------|
| 1 | false | 1 | [preview] | N | Yes |
| 2 | true | 2 | [preview] | N | Yes |
| 3 | false | 3 | [preview] | N | Yes |
| 4 | true | 2 | [preview] | N | Yes |

**Variable List**
- Standard: {first_name}, {company}, ...
- Custom (need Clay enrichment): {var_name}, ...

**Spintax Validation:** PASS / FAIL

Type `preview [1-4]` to see full copy. Otherwise, approve to continue.

---

### Step 9 — Create Sequence in Salesforge

After approval:

**Two APIs in play:**
- Core API: `https://api.salesforge.ai/public/v2`
- Multichannel API: `https://multichannel-api.salesforge.ai/public`

```
1. Validate API key
   GET /me → confirm auth works, get accountId

2. Get workspace
   GET /workspaces → list all workspaces → user confirms which one
   → save workspaceID

3. Check for name conflicts
   GET /multichannel/workspaces/{workspaceID}/sequences?limit=100
   → scan for duplicate names
   If conflict: append "v2" or ask user

4. Create sequence
   POST /multichannel/workspaces/{workspaceID}/sequences
   Body: {"name": "[Client] - [Description]", "timezone": "America/New_York"}
   → save sequenceID

5. Get email action ID
   GET /multichannel/actions?channel=email
   → find the "send email" action → save actionId

6. Get root branch
   GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/branches
   → save branchId from root branch

7. Create email nodes (one per step)
   POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions

   For each email step:
   {
     "actionId": "[email action ID from step 5]",
     "branchId": "[branch ID from step 6]",
     "waitDays": [delay in days],
     "variants": [
       {"subject": "[spintaxed subject]", "body": "<p>HTML body</p>"}
     ]
   }

   Step 1: waitDays=0 (send immediately on enrollment)
   Step 2: waitDays=2-3 (reply thread)
   Step 3: waitDays=3-4 (new thread)
   Step 4: waitDays=2-3 (reply thread)

8. Set schedule
   PUT /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule
   {
     "timezone": "America/New_York",
     "schedule": {
       "monday": {"enabled": true, "from": 8, "to": 17},
       "tuesday": {"enabled": true, "from": 8, "to": 17},
       "wednesday": {"enabled": true, "from": 8, "to": 17},
       "thursday": {"enabled": true, "from": 8, "to": 17},
       "friday": {"enabled": true, "from": 8, "to": 17},
       "saturday": {"enabled": false, "from": 0, "to": 0},
       "sunday": {"enabled": false, "from": 0, "to": 0}
     }
   }
   NOTE: from/to are integer hours (0-23), NOT "HH:MM" strings

9. Configure settings
   PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings
   {
     "plainTextEmailsEnabled": true,
     "openTrackingEnabled": false,
     "optOutLinkEnabled": false,
     "optOutTextEnabled": false,
     "ccAndBccEnabled": false,
     "trackOpportunitiesEnabled": false
   }

10. Attach sender profiles
    Read sender-cache.md → if cached, use those IDs
    If not cached:
      GET /multichannel/workspaces/{workspaceID}/sender-profiles?limit=100
      → show list → user selects → cache to sender-cache.md
    POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles
    {"senderProfileIds": ["id1", "id2"]}

11. Verify
    GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}
    GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes
    → confirm node count, subjects, bodies intact
```

### IMPORTANT: DO NOT ACTIVATE.

**Never call the /launch endpoint or set status to "active". The sequence stays in DRAFT status. Launch is always done manually by the user in the Salesforge dashboard.**

Show final confirmation: "Sequence '[name]' created in DRAFT. Go to Salesforge dashboard to review and launch."

---

## Error Handling

| Error | Response |
|---|---|
| 400 Bad Request | Check body format, required fields (see reference skill) |
| 401 Unauthorized | API key invalid — regenerate in Settings → Integrations |
| 402 Payment Required | Insufficient credits — inform user |
| 403 Forbidden | Feature not available on plan |
| 404 Not Found | Check workspaceID/sequenceID — list resources again |
| 500 Server Error | Retry once. If persistent, switch to fallback mode |
| Spam fixer fails | Fall back to manual Cyrillic fixes using character-map.md |
| Spintax validation fails | Show broken token, auto-repair, re-validate |
| User requests changes at gate | Re-run from affected step, show new approval gate |

---

## Fallback Mode

If Salesforge API calls fail (auth issues, unknown endpoints, plan restrictions):

**Switch to Manual Mode:**
1. Complete Steps 1-8 normally (spam fix, spintax, variables, HTML, validation)
2. At Step 9, instead of API calls, output:
   - Full HTML body for each email step
   - Subject lines
   - Variable list
   - Recommended sequence settings
3. User manually creates the sequence in Salesforge dashboard and pastes the copy

This ensures the skill is useful even before all API endpoints are confirmed.
