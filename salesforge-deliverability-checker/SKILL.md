---
name: salesforge-health
description: Check mailbox warmup status, monitor sender reputation, run placement tests, and recommend warmup duration before sending. Use before launching sequences to ensure deliverability.
---

# Salesforge Deliverability Checker

Check mailbox health before you send. Prevents bounces, spam folders, and reputation damage.

> **Before proceeding:** Invoke the `salesforge` reference skill to load API context.

---

## Pre-Send Health Check

Run this before activating any sequence:

### Step 1 — List Sender Profiles

```
GET /sender-profiles → list all mailboxes in workspace

For each mailbox, check:
- Status: active / warming / suspended
- Warmup progress: days warmed / target days
- Daily sending limit
- Reputation score (if available)
- Last send date
```

### Step 2 — Warmup Validation

| Warmup Days | Status | Recommendation |
|---|---|---|
| 0-7 days | 🔴 Not ready | Do NOT send. Continue warmup. |
| 8-14 days | 🟡 Risky | Send at 25% volume max (12-15 emails/day) |
| 15-21 days | 🟢 Ready | Send at 50% volume (25-50 emails/day) |
| 21+ days | ✅ Fully warmed | Send at full volume |

**Report:**
```
MAILBOX HEALTH CHECK
====================
Workspace: [Name]
Date: [YYYY-MM-DD]

| Mailbox | Warmup Days | Status | Max Daily | Recommendation |
|---------|-------------|--------|-----------|----------------|
| user1@domain.com | 24 | ✅ Ready | 50 | Full volume |
| user2@domain.com | 12 | 🟡 Risky | 15 | Reduce volume |
| user3@domain.com | 3 | 🔴 Not ready | 0 | Continue warmup |

Ready mailboxes: [N] / [Total]
Combined daily capacity: [N] emails/day
```

### Step 3 — Sequence Volume Check

Compare sequence requirements against mailbox capacity:

```
Sequence: [Name]
Contacts to enroll: [N]
Steps per contact: [N]
Total emails to send: [contacts × steps]
Estimated daily send: [based on cadence]

Available capacity: [combined daily limit from healthy mailboxes]

✅ PASS: Capacity exceeds demand
⚠️ WARNING: Capacity is tight — consider reducing daily enrollment
🔴 FAIL: Not enough warmed mailboxes — add more or wait for warmup
```

---

## DNS Health Check

### SPF / DKIM / DMARC Verification

For each sending domain, verify:

```bash
# SPF
dig TXT [domain] | grep "v=spf1"

# DKIM
dig TXT [selector]._domainkey.[domain]

# DMARC
dig TXT _dmarc.[domain]
```

**Report:**
```
DOMAIN HEALTH: [domain.com]
- SPF:   ✅ Valid (includes Salesforge IPs)
- DKIM:  ✅ Valid (key found)
- DMARC: ⚠️ Missing (recommend adding p=none for monitoring)

DOMAIN HEALTH: [domain2.com]
- SPF:   🔴 Missing (deliverability risk)
- DKIM:  🔴 Missing (high spam risk)
- DMARC: 🔴 Missing
→ ACTION: Set up DNS records before sending
```

---

## Reputation Monitoring

### Blacklist Check

Check sending IPs/domains against common blacklists:

```bash
# Check domain reputation
dig [domain].zen.spamhaus.org
dig [domain].bl.spamcop.net
dig [domain].b.barracudacentral.org
```

**Status:**
- Clean on all lists → ✅ Good
- Listed on 1 list → ⚠️ Warning — investigate, may need IP change
- Listed on 2+ lists → 🔴 Critical — pause sending, contact Salesforge support

---

## Recommendations Engine

Based on checks, output actionable recommendations:

```
DELIVERABILITY RECOMMENDATIONS
==============================

1. ✅ [N] mailboxes fully warmed — ready to send
2. ⚠️ [N] mailboxes need [X] more warmup days — hold until [date]
3. 🔴 Domain [X] missing DKIM — add record: [specific record]
4. ℹ️ Combined capacity: [N] emails/day — sequence needs [N]/day
5. ✅ No blacklist detections

VERDICT: [READY TO SEND / WAIT / FIX ISSUES FIRST]
```

---

## Caching

Store mailbox warmup status in `mailbox-cache.md` to avoid repeated checks:

```
## [Workspace Name]
- last_checked: [YYYY-MM-DD]
- mailboxes:
  - user1@domain.com: 24 days, ready
  - user2@domain.com: 12 days, warming
```

Cache expires after 3 days — re-check automatically.

---

## Error Handling

| Error | Response |
|---|---|
| Cannot reach warmup API | Fall back to manual dashboard check — tell user to verify in Salesforge UI |
| DNS lookup fails | Try alternative DNS resolver (8.8.8.8, 1.1.1.1) |
| Mailbox suspended | Flag immediately — do not attach to sequence |
| Blacklist detected | Pause all sequences using that IP/domain, alert user |
