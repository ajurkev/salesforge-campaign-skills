---
name: salesforge
description: Reference skill for working with the Salesforge API. Contains all rules for sequences, contacts, enrollments, sender profiles, workspaces, webhooks, and defaults. Use when creating or managing Salesforge campaigns, sequences, contacts, or any Salesforge API operation.
---

# Salesforge API — Rules & Reference

## Connection

- **API Type:** REST API — direct HTTP calls (no official MCP server)
- **Base URL:** `https://api.salesforge.ai` ⚠️ UNCONFIRMED — verify on first use
- **Auth:** API Key in header
- **Header:** `X-API-Key: <your-api-key>` ⚠️ UNCONFIRMED — may be `Authorization: Bearer <key>`
- **Content-Type:** `application/json`
- **API Key Location:** Salesforge → Settings → Integrations → Generate API Key

> **First-run requirement:** On first API call, test both auth header formats and confirm which works. Update this file with the confirmed format.

---

## Confirmed Capabilities (from integration analysis)

These operations are confirmed available via API (used by Clay, Make, Zapier):

### Contacts

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| Create contact | POST | `/contacts` ⚠️ | Single contact creation |
| Update contact | PUT/PATCH | `/contacts/{id}` ⚠️ | Update existing contact |
| Bulk import | POST | `/contacts/bulk` ⚠️ | Multiple contacts in one call |
| List contacts | GET | `/contacts` ⚠️ | Paginated list |
| Delete contact | DELETE | `/contacts/{id}` ⚠️ | Remove contact |

**Contact Object Fields (confirmed from Clay integration):**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string (required)",
  "company": "string",
  "job_title": "string",
  "industry": "string",
  "linkedin_url": "string",
  "phone": "string",
  "custom_variables": {
    "variable_name": "value"
  }
}
```

### Sequences

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| List sequences | GET | `/sequences` ⚠️ | All sequences in workspace |
| Get sequence | GET | `/sequences/{id}` ⚠️ | Single sequence details |
| Create sequence | POST | `/sequences` ⚠️ | New sequence with steps |
| Update sequence | PUT | `/sequences/{id}` ⚠️ | Modify existing |
| Delete sequence | DELETE | `/sequences/{id}` ⚠️ | Remove sequence |

### Enrollments

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| Enroll contact | POST | `/enrollments` ⚠️ | Add contact to sequence |
| Bulk enroll | POST | `/enrollments/bulk` ⚠️ | Multiple contacts |
| Unenroll | DELETE | `/enrollments/{id}` ⚠️ | Remove from sequence |
| Get status | GET | `/enrollments/{id}` ⚠️ | Check enrollment progress |

### Workspaces

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| List workspaces | GET | `/workspaces` ⚠️ | All available workspaces |
| Get current | GET | `/workspaces/current` ⚠️ | Active workspace |
| Switch workspace | — | Manual in dashboard | API switching unconfirmed |

### Sender Profiles / Mailboxes

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| List senders | GET | `/sender-profiles` ⚠️ | All mailboxes in workspace |
| Get sender | GET | `/sender-profiles/{id}` ⚠️ | Single sender details |
| Attach to sequence | POST | `/sequences/{id}/senders` ⚠️ | Link mailboxes to sequence |

### DNC (Do Not Contact)

| Operation | Method | Endpoint | Notes |
|---|---|---|---|
| Add to DNC | POST | `/dnc` ⚠️ | Block email/domain |
| List DNC | GET | `/dnc` ⚠️ | Current blocklist |
| Remove from DNC | DELETE | `/dnc/{id}` ⚠️ | Unblock |

---

## Sequence Structure

### Email Step Object

```json
{
  "order": 1,
  "subject": "your subject here",
  "body": "<p>HTML body here</p>",
  "wait_days": 1,
  "is_reply": false,
  "variant": false
}
```

⚠️ Field names unconfirmed — may differ from EmailBison conventions. Test on first sequence creation and update this file.

### Thread Structure (expected pattern)

| Step | is_reply | wait_days | Subject |
|------|----------|-----------|---------|
| 1 | false | 1 | Required — new thread |
| 2 | true | 2-3 | Reply to step 1 subject |
| 3 | false | 3-4 | Required — new thread |
| 4 | true | 2-3 | Reply to step 3 subject |

### Sequence Defaults — Apply Unless User Specifies Otherwise

```json
{
  "name": "[Client] - [Description]",
  "type": "email",
  "tracking": {
    "open_tracking": false,
    "click_tracking": false
  },
  "schedule": {
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "start_time": "08:00",
    "end_time": "17:00",
    "timezone": "America/New_York"
  },
  "sending_limits": {
    "max_emails_per_day": 200,
    "max_new_leads_per_day": 50
  }
}
```

---

## Variable Handling

### Built-in Fields — Auto-populated from contact record

| Field | Format |
|---|---|
| First name | `{first_name}` ⚠️ |
| Last name | `{last_name}` ⚠️ |
| Email | `{email}` ⚠️ |
| Company | `{company}` ⚠️ |
| Job title | `{job_title}` ⚠️ |

⚠️ Variable format unconfirmed — Salesforge may use `{{first_name}}`, `{first_name}`, or `[[first_name]]`. Test on first sequence and update.

### Custom Variables

Custom variables passed via contact import or Clay enrichment:
```
{pain_point}
{competitor_tool}
{industry}
{custom_first_line}
```

---

## Spintax Format

⚠️ Salesforge spintax format unconfirmed. Likely one of:
- `{option1|option2|option3}` (Bison-style)
- `{{RANDOM|option1|option2|option3}}` (Instantly-style)
- `[option1|option2|option3]` (custom)

**Test on first sequence creation and update this section.**

---

## Webhook Events (CONFIRMED)

Setup: Settings → Integrations → Webhooks → Add Webhook

| Event | Trigger |
|---|---|
| `email_sent` | Email dispatched |
| `email_opened` | Recipient opened email |
| `email_clicked` | Link clicked |
| `email_bounced` | Delivery failure |
| `reply_received` | Reply detected |

**Payload:** HTTP POST with JSON body containing event type + full contact details.

---

## Pagination

⚠️ Pagination strategy unconfirmed. Expected pattern:
- `page` and `per_page` query params
- Default: 15-25 per page
- Max: 100 per page
- Response includes `meta.last_page` or `total` count

**Always paginate. Never assume page 1 is all data.**

---

## Rate Limiting

⚠️ Not publicly documented. Recommendations:
- Add 100ms delay between sequential API calls
- Use bulk endpoints when available
- Cache sender profiles and workspace data locally
- If 429 received: wait 60s and retry

---

## Sending Limits & Quotas

| Limit | Value | Notes |
|---|---|---|
| Enrollment credits | 1 credit per contact per active sequence | Plan-dependent |
| Mailbox rotation | Automatic | Salesforge handles sender rotation |
| Daily sending limit | Configurable per sequence | Default: 200/day |
| Warmup period | 14-21 days recommended | Via Warmforge |

---

## Multi-Product Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                    SALESFORGE ECOSYSTEM                       │
├──────────────┬──────────────┬───────────────┬───────────────┤
│  Salesforge  │  Leadsforge  │  Warmforge    │  Infraforge   │
│  Sequences   │  Lead Search │  Warmup       │  Dedicated IP │
│  Contacts    │  Enrichment  │  Deliverability│  Custom DNS  │
│  Enrollments │  Lookalike   │  Reputation   │  Email Infra  │
├──────────────┼──────────────┼───────────────┼───────────────┤
│  Primeforge  │  Mailforge   │               │               │
│  Google/M365 │  Shared Infra│               │               │
│  Mailboxes   │  Mailboxes   │               │               │
└──────────────┴──────────────┴───────────────┴───────────────┘
```

**API access confirmed:** Salesforge (core), Infraforge (dedicated IP)
**Integrated via Salesforge:** Leadsforge, Warmforge, Primeforge, Mailforge

---

## Standard Sequence Creation Order

```
1. Verify workspace (GET /workspaces/current)
   If wrong: ask user to switch manually in Salesforge dashboard

2. List existing sequences (GET /sequences) → check for name conflicts

3. Create sequence (POST /sequences) → save returned sequence_id

4. Add steps to sequence (POST /sequences/{id}/steps)
   All steps in one call if supported, otherwise sequential

5. Configure schedule and sending limits

6. Attach sender profiles / mailboxes

7. STOP — show summary. Sequence is ready but PAUSED.
   DO NOT activate. Launch is always manual.
```

---

## Error Handling

| Error | Response |
|---|---|
| 401 Unauthorized | API key invalid or expired — regenerate in Settings |
| 403 Forbidden | Endpoint not available on current plan |
| 404 Not Found | Endpoint path wrong — check and update reference |
| 409 Conflict | Resource already exists (sequence name, contact email) |
| 422 Validation Error | Check field names, required fields, format |
| 429 Rate Limited | Wait 60s, retry. Reduce request frequency |
| 500 Server Error | Retry once. If persistent, check Salesforge status page |

---

## Sender Cache

Sender profile IDs are stored in `sender-cache.md` (same directory as sequence-creator skill).

**On every sequence creation:**
1. Read `sender-cache.md`
2. If workspace has cached IDs → confirm with user → skip API
3. If not cached → GET /sender-profiles → filter → cache → attach
4. Attach senders to sequence

---

## ⚠️ API Discovery Checklist

Before first production use, confirm these with the actual API:

- [ ] Base URL (`https://api.salesforge.ai` or different?)
- [ ] Auth header format (`X-API-Key` vs `Authorization: Bearer`)
- [ ] Contact field names (snake_case vs camelCase)
- [ ] Sequence step field names (`wait_days` vs `wait_in_days` vs `delay`)
- [ ] Variable format in email bodies (`{first_name}` vs `{{first_name}}`)
- [ ] Spintax format supported
- [ ] Pagination params and response shape
- [ ] Rate limit headers
- [ ] Bulk endpoint availability and batch size limits
- [ ] DNC list endpoints
- [ ] Sender profile attachment method

Update this file as each item is confirmed.
