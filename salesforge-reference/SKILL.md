---
name: salesforge
description: Reference skill for working with the Salesforge API v2. Contains all confirmed rules for sequences, contacts, enrollments, sender profiles, workspaces, webhooks, nodes, and defaults. Use when creating or managing Salesforge sequences, contacts, or any Salesforge API operation.
---

# Salesforge API v2 — Rules & Reference

**Source:** https://api.salesforge.ai/public/v2/swagger/index.html
**Spec:** https://api.salesforge.ai/public/v2/swagger/doc3.json

## Connection

- **Base URL:** `https://api.salesforge.ai/public/v2`
- **Multichannel Base URL:** `https://multichannel-api.salesforge.ai/public`
- **Auth:** `Authorization: <API_KEY>` header (ApiKeyAuth)
- **Content-Type:** `application/json`
- **API Key Location:** Salesforge → Settings → Integrations → Generate API Key

---

## Auth

### GET /me
Validates API key, returns `accountId` and `apiKeyName`.

---

## Workspaces

### GET /workspaces
List all workspaces. Query: `limit` (default 10), `offset` (default 0).

### POST /workspaces
Create workspace. Body: `{"name": "string"}` (1-100 chars, required). Returns 201.

### GET /workspaces/{workspaceID}
Get single workspace.

---

## Contacts

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
      "tagIds": ["string"],
      "customVars": {"key": "value"}
    }
  ]
}
```
**Limit:** 1-100 contacts per call. Returns 201.

### GET /workspaces/{workspaceID}/contacts/{contactID}
Get single contact.

---

## Custom Variables

### GET /workspaces/{workspaceID}/custom-vars
List custom variables. Query: `limit`, `offset`.

---

## DNC (Do Not Contact)

### POST /workspaces/{workspaceID}/dnc/bulk
Bulk create DNC entries. Body:
```json
{
  "dncs": [
    {"email": "user@example.com"},
    {"domain": "example.com"}
  ]
}
```
**Limit:** 1-1000 entries per call. Returns created count. 201.

---

## Mailboxes

### GET /workspaces/{workspaceID}/mailboxes
List mailboxes. Query params:
- `limit`, `offset`
- `statuses[]` — filter by status
- `mailbox_ids[]`, `excluded_mailbox_ids[]`
- `search` — text search
- `tag_ids[]`, `not_tag_ids[]`
- `addresses[]` — filter by email address

### GET /workspaces/{workspaceID}/mailboxes/{mailboxID}
Get mailbox details. Returns:
- `address`, `id`, `firstName`, `lastName`
- `status`, `mailboxProvider`
- `signature`, `trackingDomain`, `trackingDomainStatus`
- `dailyEmailLimit`, `disconnectReason`

### POST /workspaces/{workspaceID}/mailboxes/{mailboxID}/emails/{emailID}/reply
Reply to an email thread. Body:
```json
{
  "content": "string",
  "includeHistory": true,
  "ccs": ["email@example.com"],
  "bccs": ["email@example.com"]
}
```
Returns 204.

---

## Sequences (Multichannel API)

**Base URL:** `https://multichannel-api.salesforge.ai/public`

### GET /multichannel/workspaces/{workspaceID}/sequences
List sequences. Query: `page` (min 1), `limit` (1-100), `status` (draft|active|completed|paused).

### POST /multichannel/workspaces/{workspaceID}/sequences
Create sequence. Body:
```json
{
  "name": "string (REQUIRED)",
  "description": "string",
  "timezone": "string"
}
```
Returns 201 with sequence ID.

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}
Get sequence details.

### PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}
Update sequence (name, description, timezone).

### DELETE /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}
Delete sequence. Returns 204.

### PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/launch
Launch sequence. Returns sequence response.

### PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/status
Update status. Body:
```json
{
  "status": "active" | "paused"
}
```

---

## Sequence Nodes (Steps)

Salesforge uses a **node-based** sequence model, not a linear step array.

### GET /multichannel/actions
List available actions. Query: `channel` (email|linkedin), `name`, `page`, `limit`.

### GET /multichannel/conditions
List available conditions. Same query params as actions.

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes
List all nodes in a sequence. Query: `type` (action|condition|root|terminal), `channel`, `name`, `page`, `limit`.

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions
Create action node (email step). Body:
```json
{
  "actionId": "string (REQUIRED)",
  "branchId": "string (REQUIRED)",
  "waitDays": 0,
  "distributionStrategy": "string",
  "variants": [
    {
      "subject": "string",
      "body": "string"
    }
  ]
}
```
Returns 201.

### PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions/{nodeID}
Update action node (change subject, body, wait days, variants).

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/conditions
Create condition node. Body:
```json
{
  "branchId": "string (REQUIRED)",
  "conditionId": "string (REQUIRED)"
}
```
Returns 201.

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/{nodeID}
Get single node.

### DELETE /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/{nodeID}
Delete node. Returns 204.

---

## Sequence Branches

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/branches
List branches. Query: `page`, `limit`.

---

## Sequence Schedule

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule
Get current schedule.

### PUT /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule
Set schedule. Body:
```json
{
  "timezone": "America/New_York (REQUIRED)",
  "schedule": {
    "sunday": {"enabled": false, "from": 0, "to": 0},
    "monday": {"enabled": true, "from": 8, "to": 17},
    "tuesday": {"enabled": true, "from": 8, "to": 17},
    "wednesday": {"enabled": true, "from": 8, "to": 17},
    "thursday": {"enabled": true, "from": 8, "to": 17},
    "friday": {"enabled": true, "from": 8, "to": 17},
    "saturday": {"enabled": false, "from": 0, "to": 0}
  }
}
```
**Note:** `from`/`to` are hours 0-23 (integers), NOT "HH:MM" strings.

---

## Sequence Sender Profiles

### GET /multichannel/workspaces/{workspaceID}/sender-profiles
List all sender profiles. Query: `page`, `limit`.

### PATCH /multichannel/workspaces/{workspaceID}/sender-profiles/{senderProfileID}
Update sender profile. Body: `{"name": "string", "mailboxIds": ["string"]}`.

### DELETE /multichannel/workspaces/{workspaceID}/sender-profiles/{senderProfileID}
Delete sender profile. Returns 204.

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles
List sender profiles attached to a sequence.

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles
Attach sender profiles to sequence. Body:
```json
{
  "senderProfileIds": ["id1", "id2"]
}
```
**Minimum:** 1 sender profile required.

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles/remove
Remove sender profiles from sequence. Body:
```json
{
  "senderProfileIds": ["id1", "id2"]
}
```
**Limit:** 1-50 IDs per call.

---

## Sequence Settings

### GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings
Get sequence settings.

### PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings
Update settings. Body:
```json
{
  "ccAndBccEnabled": false,
  "bcc": "",
  "cc": "",
  "openTrackingEnabled": false,
  "optOutLinkEnabled": false,
  "optOutLinkText": "",
  "optOutText": "",
  "optOutTextEnabled": false,
  "plainTextEmailsEnabled": true,
  "trackOpportunitiesEnabled": false,
  "opportunitiesValue": 0
}
```

**Defaults (apply unless user specifies otherwise):**
- `openTrackingEnabled`: false (improves deliverability)
- `plainTextEmailsEnabled`: true
- `optOutLinkEnabled`: false (cold email best practice)
- `ccAndBccEnabled`: false
- `trackOpportunitiesEnabled`: false

---

## Enrollments

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/enrollments
Add enrollments. Body:
```json
{
  "filters": {
    "esps": ["string"],
    "hasEmail": true,
    "hasValidLinkedIn": true,
    "leadIds": ["string"],
    "tagIds": ["string"],
    "validationRunId": "string",
    "validationStatuses": ["string"]
  },
  "limit": 100
}
```
**`filters` is REQUIRED.** Use `leadIds` to enroll specific contacts.
Returns 201.

### POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/enrollments/remove
Remove enrollments. Body: `RemoveEnrollmentsRequest`. Returns 204.

---

## Validations (Email Verification)

### POST /multichannel/workspaces/{workspaceID}/validations
Start validation run. Body:
```json
{
  "filters": {
    "leadIds": ["string"],
    "tagIds": ["string"],
    "hasEmail": true,
    "searchQuery": "string",
    "withEmailOnly": true
  },
  "limit": 100
}
```
Returns 201. **Status 402 if insufficient credits.**

### GET /multichannel/workspaces/{workspaceID}/validations/{runID}/results
Get validation results summary.

---

## Webhooks

### GET /workspaces/{workspaceID}/integrations/webhooks
List webhooks. Query: `limit`, `offset`.

### POST /workspaces/{workspaceID}/integrations/webhooks
Create webhook. Body:
```json
{
  "name": "string (REQUIRED)",
  "type": "string (REQUIRED)",
  "url": "string",
  "sequenceID": "string"
}
```

**Webhook event types:**
- `email_sent`
- `email_opened`
- `link_clicked`
- `email_replied`
- `linkedin_replied`
- `contact_unsubscribed`
- `email_bounced`
- `positive_reply`
- `negative_reply`
- `label_changed`
- `dnc_added`

### GET /workspaces/{workspaceID}/integrations/webhooks/{webhookID}
Get single webhook.

---

## Pagination

**Two different patterns depending on API:**

### Core API (api.salesforge.ai)
- Uses `limit` + `offset`
- Default limit: 10
- Example: `?limit=100&offset=0`, then `?limit=100&offset=100`

### Multichannel API (multichannel-api.salesforge.ai)
- Uses `page` + `limit`
- Page minimum: 1
- Limit: 1-100
- Example: `?page=1&limit=100`, then `?page=2&limit=100`

**Always paginate. Never assume first page is all data.**

---

## Standard Sequence Creation Order

```
1. GET /me → validate API key

2. GET /workspaces → find correct workspaceID
   Or GET /workspaces/{workspaceID} if known

3. POST /multichannel/workspaces/{workspaceID}/sequences
   Body: {"name": "[Client] - [Description]", "timezone": "America/New_York"}
   → save sequenceID

4. GET /multichannel/actions?channel=email → find email action ID
   → save actionId for "send email" action

5. GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/branches
   → get root branchId

6. Create email nodes (steps):
   POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions
   For each step:
   {
     "actionId": "[email action ID]",
     "branchId": "[branch ID]",
     "waitDays": [delay],
     "variants": [{"subject": "...", "body": "<p>HTML</p>"}]
   }

7. PUT /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule
   Set Mon-Fri, 8-17, timezone

8. PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings
   Set plainTextEmailsEnabled=true, openTrackingEnabled=false

9. Attach sender profiles:
   Read sender-cache.md → if cached, use those IDs
   If not cached: GET sender-profiles → filter → cache
   POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles
   {"senderProfileIds": ["id1", "id2"]}

10. Verify:
    GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID} → confirm setup
    GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes → verify steps

11. STOP — sequence is in DRAFT status.
    DO NOT launch. DO NOT call /launch endpoint.
    Launch is always manual by the user.
```

---

## Key Salesforge API Traits

| Feature | How It Works |
|---|---|
| API structure | Dual API (core + multichannel) |
| Steps model | Node-based (actions + conditions + branches) |
| Schedule format | Integer hours (0-23), not "HH:MM" strings |
| Pagination | Core: `limit`+`offset` / Multichannel: `page`+`limit` |
| Auth | `Authorization: <API_KEY>` header |
| Sender attachment | `senderProfileIds` (profiles, not individual mailboxes) |
| Sequence status | draft → active → paused → completed |
| A/B variants | `variants` array on action node |
| Multichannel | Email + LinkedIn actions |

---

## Error Handling

| Code | Meaning | Response |
|---|---|---|
| 400 | Bad Request | Check body format, required fields |
| 401 | Unauthorized | API key invalid — regenerate |
| 402 | Payment Required | Insufficient credits (validation, enrichment) |
| 403 | Forbidden | Feature not on current plan |
| 404 | Not Found | Check workspaceID, sequenceID, nodeID |
| 500 | Server Error | Retry once. If persistent, check status page |

---

## Sender Cache

Store sender profile IDs per workspace in `sender-cache.md`:

```markdown
## [Workspace Name]
- workspace_id: [ID]
- sender_profile_ids: [id1, id2, id3]
- last_updated: [YYYY-MM-DD]
```

**On every sequence creation:**
1. Read sender-cache.md
2. If cached → confirm with user → attach directly
3. If not cached → GET /sender-profiles → show list → user selects → cache → attach
