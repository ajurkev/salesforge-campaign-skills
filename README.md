# Salesforge MCP Skills for Claude Code

Create multichannel sequences in Salesforge directly from Claude Code. Paste copy → spam check → spintax → live sequence in DRAFT. Works with the official Salesforge MCP server.

Created by [RevSculpt](https://revsculpt.com)

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| `salesforge-reference` | `/salesforge` | API rules, confirmed traps, variable format, branch chaining, defaults |
| `salesforge-sequence-creator` | `/salesforge-sequence` | **Main pipeline:** paste copy → spam fix → spintax → push to Salesforge via MCP |

**Everything else (contacts, enrollment, deliverability, sender profiles) is handled natively by the Salesforge MCP tools** — no custom skills needed.

## How It Works

```
1. Paste email copy into Claude Code
2. /salesforge-sequence processes it:
   Parse → Spintax → Spam Check → Spam Fix → Variables → HTML → Validate
3. You review the approval gate
4. MCP pushes to Salesforge: create sequence → add nodes → set schedule → attach senders
5. Sequence appears in DRAFT — you launch manually
```

## Requires

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Salesforge MCP server configured in Claude Code — [setup guide](https://help.salesforge.ai/en/articles/10333582-salesforge-mcp-server-connect-with-ai-assistants)
- Salesforge API key (Settings → Integrations → API Key)

## Installation

```bash
git clone https://github.com/ajurkev/revsculpt-salesforge-secret-sauce.git
cp -r revsculpt-salesforge-secret-sauce/salesforge-* ~/.claude/skills/
```

## Key Traps Documented

Things the Swagger docs don't tell you — all solved in the reference skill:

1. **`metadata.message`** not `body` — email body field is nested, silent failure if wrong
2. **Integer IDs** — `actionId`, `branchId`, `senderProfileIds` are integers, not strings
3. **`{{double_braces}}`** for variables — `{{first_name}}`, NOT `{first_name}`
4. **Branch chaining** — each new node creates a new branch, must re-fetch before adding next node
5. **`waitDays` vs `wait_in_minutes`** — create uses days, update uses minutes
6. **Schedule disabled days** — `"from": 0, "to": 0` returns 422, use `"to": 23`
7. **Two APIs** — Core API uses `limit+offset`, Multichannel uses `page+limit`

## Salesforge MCP Tools Used

| MCP Tool | What It Does |
|----------|-------------|
| `get_me` | Validate API key |
| `list_workspaces` | Find workspace ID |
| `bulk_create_contacts` | Upload contacts (up to 100/call) |
| `create_sequence` | Create sequence in DRAFT |
| `list_sequence_branches` | Get branch ID for node chaining |
| `create_action_node` | Add email/LinkedIn step |
| `update_action_node` | Fix copy or variables post-creation |
| `update_sequence_schedule` | Set Mon-Fri, 8-17 |
| `update_sequence_settings` | Plain text, no tracking |
| `list_sender_profiles` | Find sender IDs |
| `assign_sender_profiles_to_sequence` | Attach senders |
| `enroll_contacts` | Enroll contacts into sequence |

## License

MIT

---

Built by [RevSculpt](https://revsculpt.com)
