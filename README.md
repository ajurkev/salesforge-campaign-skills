# Salesforge Campaign Skills for Claude Code

Orchestrate your entire Salesforge campaign workflow from Claude Code — sequence creation, contact upload, enrollment, deliverability checks. All without leaving the terminal.

Created by [RevSculpt](https://revsculpt.com)

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `salesforge-reference` | `/salesforge` | API rules, endpoints, variable mapping, defaults |
| `salesforge-sequence-creator` | `/salesforge-sequence` | **Main pipeline:** paste copy → create sequence in Salesforge (paused) |
| `salesforge-contact-manager` | `/salesforge-contacts` | Import contacts from local CSV or Clay export. Validate, dedupe, manage DNC |
| `salesforge-enrollment-manager` | `/salesforge-enroll` | Enroll contacts into sequences, monitor, pause/resume |
| `salesforge-deliverability-checker` | `/salesforge-health` | Mailbox warmup status, sender reputation, DNS health |

## How It Works

```
Check Deliverability               → /salesforge-health
    ↓
Import Contacts from CSV or Clay   → /salesforge-contacts
    ↓
Create Sequence (paste copy)       → /salesforge-sequence
    ↓
Enroll Contacts into Sequence      → /salesforge-enroll
    ↓
Launch manually in Salesforge dashboard
```

## Installation

```bash
# Clone
git clone https://github.com/ajurkev/salesforge-campaign-skills.git

# Copy all skills to your project
cp -r salesforge-campaign-skills/salesforge-* /path/to/project/.claude/skills/

# Or to global Claude Code skills
cp -r salesforge-campaign-skills/salesforge-* ~/.claude/skills/
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Salesforge account with API access
- Salesforge API key (Settings → Integrations → API Key)

## API Key Setup

1. Go to **Settings → Integrations** in Salesforge
2. Click **Generate API Key**
3. Store the key — it's used in the `Authorization` header for all API calls

## API Coverage

All endpoints come from the official [Salesforge API v2 Swagger spec](https://api.salesforge.ai/public/v2/swagger/index.html). Two base URLs:

- **Core API:** `https://api.salesforge.ai/public/v2` — workspaces, contacts, mailboxes, webhooks, DNC
- **Multichannel API:** `https://multichannel-api.salesforge.ai/public` — sequences, nodes, enrollments, sender profiles, schedules

## Development Status

| Phase | Status |
|-------|--------|
| Phase 1: Reference + Sequence Creator + Enrollment | ✅ Built |
| Phase 2: Contact Manager + Deliverability | ✅ Built |
| Phase 3: Lead Search + Enrichment | 🔜 Planned |
| Phase 4: DNS + Domain Setup | 🔜 Planned |
| Phase 5: Analytics + Reporting | 🔜 Planned |

## License

MIT

---

Built by [RevSculpt](https://revsculpt.com) — part of [Pipeclaw](https://pipeclaw.ai), the AI-native outbound orchestration and execution agent.
