# Salesforge Campaign Skills for Claude Code

Modular Claude Code skills for automating cold email campaign setup via the Salesforge API. Paste copy → spam check → spintax → deploy sequence — without leaving the terminal.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `salesforge-reference` | `/salesforge` | API rules, endpoints, variable mapping, defaults |
| `salesforge-sequence-creator` | `/salesforge-sequence` | **Main pipeline:** copy → spam fix → spintax → create sequence (paused) |
| `salesforge-contact-manager` | `/salesforge-contacts` | Import, enrich, validate contacts. Manage DNC lists |
| `salesforge-enrollment-manager` | `/salesforge-enroll` | Enroll contacts into sequences, monitor, pause/resume |
| `salesforge-deliverability-checker` | `/salesforge-health` | Warmforge warmup status, sender reputation, placement tests |

## Architecture

```
Contact Search (Leadsforge)
    ↓
Enrich Data (Leadsforge)
    ↓
Import Contacts (salesforge-contact-manager)
    ↓
Write Copy (your existing copy-writer / spintax-creator skills)
    ↓
Create Sequence (salesforge-sequence-creator) ← MAIN PIPELINE
    ↓
Enroll & Monitor (salesforge-enrollment-manager)
    ↓
Launch manually in Salesforge dashboard
```

## Installation

```bash
# Clone
git clone https://github.com/YOUR_ORG/salesforge-campaign-skills.git

# Copy skills to Claude Code
cp -r salesforge-campaign-skills/salesforge-reference ~/.claude/skills/
cp -r salesforge-campaign-skills/salesforge-sequence-creator ~/.claude/skills/
cp -r salesforge-campaign-skills/salesforge-contact-manager ~/.claude/skills/
cp -r salesforge-campaign-skills/salesforge-enrollment-manager ~/.claude/skills/
cp -r salesforge-campaign-skills/salesforge-deliverability-checker ~/.claude/skills/

# Or copy to project-level skills
cp -r salesforge-campaign-skills/salesforge-* /path/to/project/.claude/skills/
```

## Prerequisites

- Claude Code CLI
- Python 3.x with Playwright (`pip install playwright && playwright install chromium`)
- Salesforge API key (Settings → Integrations → API Key)
- Salesforge workspace with active mailboxes

## API Key Setup

Generate your API key in Salesforge:
1. Go to **Settings → Integrations**
2. Click **Generate API Key**
3. Store the key — you'll need it for API calls

> **Note:** Salesforge does not currently provide an official MCP server. These skills use direct HTTP API calls. If/when an official MCP becomes available, the reference skill will be updated.

## Compatibility

Works alongside the [Email Bison Campaign Skills](https://github.com/geeky-rambo/-claude-campaign-skills) — same spam-fixer and spintax-creator skills are reused. The sequence-creator orchestrator chains them automatically.

## Development Status

| Phase | Status |
|-------|--------|
| Phase 1: Reference + Sequence Creator + Enrollment | ✅ Built |
| Phase 2: Contact Manager + Deliverability | ✅ Built |
| Phase 3: Leadsforge Search + Infraforge DNS | 🔜 Planned |

## API Documentation Status

Salesforge does not publish a comprehensive public API reference. Endpoint specs in these skills are derived from:
- Official integration guides (Clay, Make, Zapier)
- Webhook documentation
- Help center articles
- Live API testing

Endpoints marked with `⚠️ UNCONFIRMED` need validation against the actual API. Contact Salesforge support (hey@salesforge.ai) or request OpenAPI spec for full coverage.

## License

MIT
