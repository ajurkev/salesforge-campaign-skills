---
name: salesforge-enroll
description: Enroll contacts into Salesforge sequences, monitor active enrollments, pause/resume, unenroll, and track performance via webhooks. Use after contacts are imported and a sequence is created.
---

# Salesforge Enrollment Manager

Enroll contacts → monitor → pause/adjust → report.

> **Before proceeding:** Invoke the `salesforge` reference skill to load API rules.

---

## Enrollment Workflow

### Step 1 — Select Sequence & Contacts

```
1. GET /sequences → list all sequences in workspace
   Show: name, step count, status (active/paused), enrolled count

2. User selects target sequence

3. Determine contact source:
   a) Contact IDs from recent import (salesforge-contacts output)
   b) Existing contacts in workspace (GET /contacts with filters)
   c) CSV/list of email addresses to match against existing contacts
```

---

### Step 2 — Pre-Enrollment Checks

Before enrolling, validate:

1. **Sequence is active** — warn if paused (contacts queue but don't send)
2. **Contacts have required fields** — check variables used in sequence steps
3. **No duplicate enrollments** — check if contacts already in this sequence
4. **DNC cross-check** — one final check against DNC list
5. **Credit check** — 1 enrollment credit per contact per active sequence

**Report:**
```
Sequence: [Name] ([N] steps)
Contacts ready: [N]
Already enrolled: [N] (skipped)
Missing required vars: [N] (flagged)
Estimated credits: [N]
```

Ask user to confirm.

---

### Step 3 — Enroll

```
1. If ≤ 50 contacts:
   POST /enrollments for each contact

2. If > 50 contacts:
   POST /enrollments/bulk

3. Track results:
   - Enrolled: [N]
   - Skipped: [N] (duplicate, DNC, missing fields)
   - Failed: [N] with reasons
```

---

### Step 4 — Monitor (Optional)

If user wants to check status:

```
GET /enrollments?sequence_id={id}&status={status}

Status options:
- active — currently progressing through steps
- completed — finished all steps
- paused — manually paused
- bounced — email bounced
- replied — received reply (auto-paused)
- unsubscribed — opted out
```

**Summary report:**
```
Sequence: [Name]
Total enrolled: [N]
Active: [N]
Completed: [N]
Replied: [N] (🎉)
Bounced: [N] (⚠️ flag if > 5%)
Unsubscribed: [N]
```

---

## Bulk Operations

### Pause All Enrollments

```
GET /enrollments?sequence_id={id}&status=active
→ For each: PATCH /enrollments/{id} {"status": "paused"}
```

### Resume All Enrollments

```
GET /enrollments?sequence_id={id}&status=paused
→ For each: PATCH /enrollments/{id} {"status": "active"}
```

### Unenroll All

```
GET /enrollments?sequence_id={id}&status=active
→ For each: DELETE /enrollments/{id}
```

⚠️ All bulk operations are destructive — always confirm with user first.

---

## Webhook Monitoring

If webhooks are configured (Settings → Integrations → Webhooks):

| Event | Action |
|---|---|
| `email_bounced` | Flag contact, check bounce rate. If >5%, pause sequence and alert. |
| `reply_received` | Auto-pause enrollment. Flag for manual follow-up. |
| `email_opened` | Track engagement. No action needed. |
| `email_clicked` | Track engagement. Flag high-intent contacts. |

---

## Performance Report

Generate after sequence has been running:

```
SEQUENCE PERFORMANCE: [Name]
Period: [start] - [end]

Enrolled:    [N]
Sent:        [N] emails across [N] contacts
Opened:      [N] ([X]% open rate)
Clicked:     [N] ([X]% click rate)
Replied:     [N] ([X]% reply rate)
Bounced:     [N] ([X]% bounce rate)
Unsubscribed:[N]

Reply breakdown:
- Positive:  [N]
- Negative:  [N]
- OOO:       [N]

Top performing step: Email [N] ([X]% reply rate)
Worst performing:   Email [N] ([X]% reply rate)
```

⚠️ Analytics endpoint unconfirmed — may need to aggregate from webhook events or export from Salesforge dashboard.

---

## Error Handling

| Error | Response |
|---|---|
| 409 Already enrolled | Skip, count in report |
| 422 Missing required field | Flag contact, skip, suggest enrichment |
| 429 Rate limited | Wait 60s, retry remaining batch |
| Sequence not found | Verify sequence_id, list sequences again |
| Insufficient credits | Show credit count, ask user to upgrade or reduce batch |
| High bounce rate (>5%) | Auto-pause sequence, alert user, suggest list cleaning |
