# Salesforge Webhook Events Reference

## Setup

Settings → Integrations → Webhooks → Add Webhook

## Event Types

| Event | Trigger | Auto-Action |
|---|---|---|
| `email_sent` | Email dispatched to recipient | Log send count |
| `email_opened` | Recipient opened email | Track engagement |
| `email_clicked` | Link in email clicked | Flag high-intent |
| `email_bounced` | Delivery failure | Flag contact, check bounce rate |
| `reply_received` | Reply detected in inbox | Auto-pause enrollment, flag for follow-up |

## Expected Payload Structure

⚠️ Exact schema unconfirmed — update after first webhook test.

```json
{
  "event": "reply_received",
  "timestamp": "2026-04-03T12:00:00Z",
  "contact": {
    "id": "contact_123",
    "email": "prospect@company.com",
    "first_name": "John",
    "last_name": "Smith",
    "company": "Acme Corp"
  },
  "sequence": {
    "id": "seq_456",
    "name": "Q2 Outbound Tier A",
    "step": 2
  },
  "email": {
    "subject": "Re: quick question",
    "body_preview": "Hi, thanks for reaching out..."
  }
}
```

## Alerting Rules

| Condition | Alert Level | Action |
|---|---|---|
| Bounce rate > 5% | 🔴 Critical | Pause sequence immediately |
| Bounce rate 3-5% | 🟡 Warning | Monitor closely, consider pausing |
| Reply rate > 10% | 🟢 Positive | Campaign performing well |
| Unsubscribe spike | 🟡 Warning | Review messaging, check list quality |
| Zero opens after 100 sends | 🔴 Critical | Deliverability issue — check mailbox health |
