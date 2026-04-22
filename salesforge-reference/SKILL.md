---
name: salesforge
description: Reference skill for working with the Salesforge Multichannel API. Contains all confirmed rules for sequences, contacts, enrollments, sender profiles, workspaces, webhooks, nodes, and defaults. Use when creating or managing Salesforge sequences, contacts, or any Salesforge API operation.
---

# Salesforge Multichannel API — Rules & Reference

**Source:** https://api.salesforge.ai/public/v2/swagger/index.html
**Spec:** https://api.salesforge.ai/public/v2/swagger/doc3.json
**Last verified:** April 2026

## Connection

- **Base URL:** `https://multichannel-api.salesforge.ai/public/multichannel`
- **Auth:** `Authorization: <API_KEY>` header — plain key, NO Bearer prefix
- **Content-Type:** `application/json`
- **API Key Location:** Salesforge → Settings → Integrations → Generate API Key

> **CONFIRMED:** The base URL includes `/multichannel` at the end. The Salesforge dashboard uses a different URL pattern (`/api/workspaces/...` with JWT) — ignore that, always use the documented path with API key auth.

---

## Auth

### GET https://api.salesforge.ai/public/v2/me
Validates API key, returns `accountId` and `apiKeyName`. This is the only endpoint on the core API base URL you need.

---

## Workspaces

### GET https://api.salesforge.ai/public/v2/workspaces
List all workspaces. Query: `limit` (default 10), `offset` (default 0).

---

## Contacts

All contact endpoints use the core API base: `https://api.salesforge.ai/public/v2`

### GET /workspaces/{workspaceID}/contacts
List contacts. Query params:
- `limit`, `offset` — pagination
- `tag_ids[]` — filter by tags
- `not_in_sequence_id` — exclude contacts already in a sequence
- `validation_statuses[]` — filter by validation status

### POST /workspaces/{workspaceID}/contacts
Create single contact. Body:
```json
{
  "firstName": "string (REQUIRED)",
  "lastName": "string",
  "email": "string",
  "linkedinUrl": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"],
  "tagIds": ["string"],
  "customVars": {"key": "value"}
}
```
Returns 201.

### POST /workspaces/{workspaceID}/contacts/bulk
Bulk create contacts. Body:
```json
{
  "contacts": [
    {
      "firstName": "string (REQUIRED)",
      "lastName": "string",
      "email": "string",
      "linkedinUrl": "string",
      "company": "string",
      "position": "string",
      "tags": ["string"],
      "customVars": {"key": "value"}
    }
  ]
}
```
**Limit:** 1-100 contacts per call. Returns 201.

> **CONFIRMED:** Tags passed as `"tags": ["my-tag"]` are created automatically. However, `tagIds` will NOT be populated — use the `tags` string array for filtering contacts by tag name when paginating.

### GET /workspaces/{workspaceID}/contacts/{contactID}
Get single contact.

---

## DNC (Do Not Contact)

### POST /workspaces/{workspaceID}/dnc/bulk
Bulk create DNC entries. Body:
```json
{
  "dncs": ["user@example.com", "example.com"]
}
```
**CRITICAL:** `dncs` is **string[]** (plain email addresses or domains), NOT objects.
**Limit:** 1-1000 entries per call. Returns `{"created": N}`. 201.

---

## Mailboxes

### GET /workspaces/{workspaceID}/mailboxes
List mailboxes. Uses core API base. Query params:
- `limit`, `offset`
- `statuses[]` — filter by status
- `search` — text search

---

## Sequences

All sequence endpoints use: `https://multichannel-api.salesforge.ai/public/multichannel`

### GET /workspaces/{workspaceID}/sequences
List sequences. Query: `page` (min 1), `limit` (1-100), `status` (draft|active|completed|paused).

> **CONFIRMED:** Response uses `"sequences"` key (not `"data"`).

### POST /workspaces/{workspaceID}/sequences
Create sequence. Body:
```json
{
  "name": "string (REQUIRED)",
  "description": "string",
  "timezone": "string (REQUIRED, IANA format e.g. America/New_York)"
}
```
**Both `name` and `timezone` are required.** Returns 201 with sequence ID (**integer**).

### GET /workspaces/{workspaceID}/sequences/{sequenceID}
Get sequence details.

### PATCH /workspaces/{workspaceID}/sequences/{sequenceID}
Update sequence (name, description, timezone).

### DELETE /workspaces/{workspaceID}/sequences/{sequenceID}
Delete sequence. Returns 204.

### PATCH /workspaces/{workspaceID}/sequences/{sequenceID}/status
Update status. Body: `{"status": "active" | "paused"}`

---

## Sequence Nodes (Steps)

Salesforge uses a **node-based** sequence model with **branch chaining**.

### GET /actions
List available actions. Query: `channel` (email|linkedin), `name`, `page`, `limit`.

> **CONFIRMED:** Email send action has `id: 3`. This is consistent across accounts.

### GET /workspaces/{workspaceID}/sequences/{sequenceID}/nodes
List all nodes in a sequence. Query: `type` (action|condition|root|terminal), `channel`, `name`, `page`, `limit`.

### GET /workspaces/{workspaceID}/sequences/{sequenceID}/branches
List branches. Query: `page`, `limit`.

> **CONFIRMED:** Response uses `"branches"` key.

### POST /workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions
Create action node (email step). Body:
```json
{
  "actionId": 3,
  "branchId": 73824,
  "waitDays": 0,
  "distributionStrategy": "equal",
  "variants": [
    {
      "isEnabled": true,
      "exposureInPercentage": 100,
      "metadata": {
        "name": "Variant A",
        "subject": "{{spintax subject | option 2 | option 3}}",
        "message": "<p>Hey {{first_name}},</p><p><br></p><p>{{Body spintax option 1 | option 2}}</p>"
      }
    }
  ]
}
```

**CRITICAL TYPES:**
- `actionId`: **integer** — use `3` for email (confirmed)
- `branchId`: **integer** — get from GET .../branches
- `waitDays`: **integer** (0 = send immediately)

**CRITICAL — BRANCH CHAINING:**
Each new node creates a NEW branch after it. To add multiple steps:
1. Get branches → use LAST branch ID for first node
2. Create node 1 → new branch is created
3. Get branches again → use the NEW last branch ID for node 2
4. Create node 2 → another new branch is created
5. Get branches again → use newest branch for node 3
6. Repeat

**This is the #1 gotcha.** If you reuse the same branchId for multiple nodes, the API returns 500.

### PATCH /workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions/{nodeID}
Update action node. Body:
```json
{
  "variants": [
    {
      "id": 33050,
      "isEnabled": true,
      "exposureInPercentage": 100,
      "metadata": {
        "name": "Variant A",
        "subject": "updated subject",
        "message": "<p>updated body</p>"
      }
    }
  ]
}
```
**NOTE:** To update wait time, use `wait_in_minutes` (NOT waitDays). 1 day = 1440 minutes.

### DELETE /workspaces/{workspaceID}/sequences/{sequenceID}/nodes/{nodeID}
Delete node. Returns 204.

---

## Spintax & Variables

**CONFIRMED FORMAT (April 2026):**

- **Spintax:** `{{option 1 | option 2 | option 3 | option 4}}` — double curly braces
- **Variables:** `{{first_name}}`, `{{last_name}}`, `{{company}}` — double curly braces
- **Sender name:** Pulled from mailbox settings automatically — do NOT include a signature line in the email body

Spintax and variables both use `{{ }}`. Salesforge differentiates them internally. A block with `|` is spintax; without `|` is a variable.

**HTML body format:**
- Each paragraph: `<p>text</p>`
- Blank line between paragraphs: `<p><br></p>`
- No inline CSS, no classes, no styling
- No em-dashes or special unicode — use plain ASCII to avoid API 500 errors

---

## Sequence Schedule

### GET /workspaces/{workspaceID}/sequences/{sequenceID}/schedule
Get current schedule.

### PUT /workspaces/{workspaceID}/sequences/{sequenceID}/schedule
Set schedule. Body:
```json
{
  "timezone": "America/New_York",
  "schedule": {
    "sunday": {"enabled": false, "from": 0, "to": 23},
    "monday": {"enabled": true, "from": 8, "to": 17},
    "tuesday": {"enabled": true, "from": 8, "to": 17},
    "wednesday": {"enabled": true, "from": 8, "to": 17},
    "thursday": {"enabled": true, "from": 8, "to": 17},
    "friday": {"enabled": true, "from": 8, "to": 17},
    "saturday": {"enabled": false, "from": 0, "to": 23}
  }
}
```
**TRAP:** `to` must be greater than `from` — even on disabled days. Use `"from": 0, "to": 23` for disabled days.

---

## Sequence Settings

### PATCH /workspaces/{workspaceID}/sequences/{sequenceID}/settings
```json
{
  "plainTextEmailsEnabled": true,
  "openTrackingEnabled": false,
  "optOutLinkEnabled": false,
  "optOutTextEnabled": false,
  "ccAndBccEnabled": false,
  "trackOpportunitiesEnabled": false
}
```

---

## Sender Profiles

> **CONFIRMED:** Sender profiles can only be **created** in the Salesforge dashboard. The API supports GET, PATCH, DELETE, and attaching to sequences — but NOT creating new profiles.

### GET /workspaces/{workspaceID}/sender-profiles
List all sender profiles. Response uses `"profiles"` key (not `"senderProfiles"`).

### POST /workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles
Attach sender profiles to sequence. Body:
```json
{
  "senderProfileIds": [5822, 5823]
}
```
**CRITICAL:** `senderProfileIds` is **integer[]**, NOT string[].

### POST /workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles/remove
Remove sender profiles from sequence. Body: `{"senderProfileIds": [5822]}`

---

## Enrollments

### POST /workspaces/{workspaceID}/sequences/{sequenceID}/enrollments
Add enrollments. Body:
```json
{
  "filters": {
    "leadIds": ["contact_id_1", "contact_id_2"],
    "hasEmail": true
  },
  "limit": 500
}
```
**`filters` is REQUIRED.** Use `leadIds` to enroll specific contacts. Batch in groups of 500.

---

## Webhooks

Webhooks use core API base: `https://api.salesforge.ai/public/v2`

### POST /workspaces/{workspaceID}/integrations/webhooks
```json
{
  "name": "string (REQUIRED)",
  "type": "string (REQUIRED)",
  "url": "string",
  "sequenceID": "string"
}
```
Event types: `email_sent`, `email_opened`, `link_clicked`, `email_replied`, `email_bounced`, `positive_reply`, `negative_reply`, `contact_unsubscribed`, `label_changed`, `dnc_added`

---

## Standard Sequence Creation Order (CONFIRMED)

```
1. GET /me (core API) → validate API key

2. GET /workspaces (core API) → find workspaceID

3. POST /workspaces/{wks}/sequences → create sequence
   Body: {"name": "...", "timezone": "America/New_York"}
   → save sequenceID (integer)

4. GET /actions?channel=email → get email actionId (usually 3)

5. GET /workspaces/{wks}/sequences/{seq}/branches
   → get LAST branch ID

6. For EACH email step:
   a. POST /workspaces/{wks}/sequences/{seq}/nodes/actions
      Body: {"actionId": 3, "branchId": [LAST_BRANCH], "waitDays": N, ...}
   b. GET /workspaces/{wks}/sequences/{seq}/branches
      → get NEW last branch ID (branch chaining!)
   c. Use new branch ID for next step

7. PUT /workspaces/{wks}/sequences/{seq}/schedule
   → Mon-Fri 8-17

8. PATCH /workspaces/{wks}/sequences/{seq}/settings
   → plainText=true, openTracking=false

9. GET /workspaces/{wks}/sender-profiles
   → find profile IDs (profiles must be created in dashboard first)
   POST /workspaces/{wks}/sequences/{seq}/sender-profiles
   → attach profiles

10. Upload contacts:
    POST /workspaces/{wks}/contacts/bulk (core API, batches of 100)
    → tag each batch for later enrollment

11. Enroll contacts:
    Paginate contacts by tag → collect IDs
    POST /workspaces/{wks}/sequences/{seq}/enrollments
    → enroll by leadIds in batches of 500

12. STOP — sequence is DRAFT. Never launch via API.
```

---

## Key Traits

| Feature | How It Works |
|---|---|
| Base URL | `https://multichannel-api.salesforge.ai/public/multichannel` |
| Auth | `Authorization: <API_KEY>` — no Bearer prefix |
| Steps model | Node-based with branch chaining |
| IDs | `actionId`, `branchId`, `senderProfileIds` are **integers** |
| Email body field | `variants[].metadata.message` |
| Subject field | `variants[].metadata.subject` |
| Spintax format | `{{option 1 \| option 2}}` — double curly braces |
| Variable format | `{{first_name}}` — double curly braces |
| Create wait | `waitDays` (integer) |
| Update wait | `wait_in_minutes` (integer, 1 day = 1440) |
| Schedule | Integer hours (0-23) |
| Sender profiles | Create in dashboard, attach via API |
| Contacts | Upload via core API (`api.salesforge.ai/public/v2`) |
| Enrollments | Filter by `leadIds`, batch 500 |
| Sequence status | draft → active → paused → completed |
| HTML bodies | `<p>text</p>` + `<p><br></p>` for spacing, no special chars |

---

## Gotchas & Traps (Battle-Tested)

1. **Branch chaining** — each node creates a new branch. Always re-fetch branches before adding the next node.
2. **No sender profile creation via API** — must create in dashboard first.
3. **Em-dashes and unicode** cause 500 errors in email bodies — use plain ASCII only.
4. **Sender profiles response** uses `"profiles"` key, not `"senderProfiles"`.
5. **Sequences response** uses `"sequences"` key, not `"data"`.
6. **Core API's PUT /sequences/{id}/steps** only updates existing steps, cannot add new ones. Always use multichannel nodes API for step creation.
7. **Tags** passed in contact bulk upload are created automatically but `tagIds` won't be populated in the response. Filter contacts by iterating and checking the `tags` string array.
8. **Disabled schedule days** still need valid `from`/`to` values. Use `"from": 0, "to": 23`.

---

## MCP Integration

Salesforge also offers an MCP server for Claude Code:

```bash
claude mcp add salesforge \
  --transport http \
  --header "X-Salesforge-Key: YOUR_API_KEY" \
  --scope project \
  salesforge \
  https://mcp.salesforge.ai/mcp
```

Restart Claude Code after adding. The MCP provides direct tool access to all Salesforge operations.
