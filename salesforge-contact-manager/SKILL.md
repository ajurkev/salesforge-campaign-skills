---
name: salesforge-contacts
description: Import, enrich, validate contacts for Salesforge sequences. Manage DNC (Do Not Contact) lists. Supports CSV import, Clay enrichment mapping, and bulk operations. Use before enrolling contacts into sequences.
---

# Salesforge Contact Manager

Import contacts, enrich with Leadsforge, validate emails, and manage DNC lists.

> **Before proceeding:** Invoke the `salesforge` reference skill to load API rules and field mappings.

---

## Workflow

### Step 1 — Determine Input Source

Ask user for contact source:

| Source | Action |
|---|---|
| **CSV file** | Read file, map columns to Salesforge fields |
| **Clay export** | Map Clay columns (usually pre-enriched) |
| **Apollo export** | Map Apollo fields to Salesforge format |
| **Manual paste** | Parse structured text (name, email, company) |
| **Leadsforge search** | Search and import directly |

---

### Step 2 — Field Mapping

Map source columns to Salesforge contact fields:

| Salesforge Field | Required | Common Source Names |
|---|---|---|
| `email` | **YES** | Email, Email Address, email_address |
| `first_name` | Yes | First Name, firstName, first |
| `last_name` | Yes | Last Name, lastName, last |
| `company` | Recommended | Company, Company Name, company_name |
| `job_title` | Recommended | Title, Job Title, job_title, Position |
| `industry` | Optional | Industry, Vertical |
| `linkedin_url` | Optional | LinkedIn, LinkedIn URL, linkedin |
| `phone` | Optional | Phone, Phone Number, mobile |

**Custom variables** (for personalization):
Any additional columns become custom variables automatically.
Examples: `pain_point`, `competitor_tool`, `custom_first_line`, `tech_stack`

Show the mapping to user and ask for confirmation before importing.

---

### Step 3 — Validate

Before import, check:

1. **Email format validation** — reject malformed emails
2. **Duplicate detection** — flag duplicate emails within the list
3. **DNC check** — cross-reference against DNC list if available
4. **Required field check** — flag rows missing email (minimum required)
5. **Encoding check** — ensure UTF-8, no broken characters

**Report:**
```
Total rows: [N]
Valid: [N] (ready to import)
Invalid email: [N] (skipped)
Duplicates: [N] (first occurrence kept)
On DNC list: [N] (skipped)
Missing required fields: [N] (skipped)
```

Ask user to confirm before proceeding.

---

### Step 4 — Import to Salesforge

```
1. Verify workspace (GET /workspaces/current)

2. Import contacts:
   - If ≤ 50 contacts: individual POST /contacts for each
   - If > 50 contacts: POST /contacts/bulk (batch import)

3. Track results:
   - Imported: [N]
   - Skipped (already exists): [N]
   - Failed: [N] with reasons

4. Return imported contact IDs for enrollment
```

---

### Step 5 — Enrichment (Optional)

If user requests enrichment via Leadsforge:

```
1. For each contact missing key fields:
   - POST /leadsforge/enrich ⚠️ (endpoint unconfirmed)
   - Fields to enrich: email, phone, linkedin_url, company size, industry

2. Cost estimation before running:
   - "[N] contacts × [cost/credit] = estimated [total] credits"
   - Ask user to confirm

3. Update contacts with enriched data
```

---

## DNC List Management

### Add to DNC

```
POST /dnc
{
  "type": "email" | "domain",
  "value": "user@example.com" | "example.com"
}
```

### Bulk DNC Import

Read from CSV or paste:
1. Parse emails/domains
2. Classify: email addresses vs. full domains
3. POST each to DNC endpoint
4. Report: "[N] emails and [N] domains added to DNC"

### DNC Cross-Check

Before any import:
1. GET /dnc → fetch current DNC list (paginate all)
2. Cross-reference import list
3. Remove matches
4. Report what was filtered

---

## Error Handling

| Error | Response |
|---|---|
| 409 Contact exists | Skip, count as "already imported" |
| 422 Invalid email | Skip row, add to error report |
| 429 Rate limited | Wait 60s, retry batch |
| Bulk import partially fails | Report which rows failed, offer retry for failed subset |
| Enrichment credit insufficient | Show remaining credits, ask user to top up or skip |
