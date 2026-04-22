"""
WEBINAR DEMO: Launch 50 multichannel campaigns in Salesforge via MCP.
Run this BEFORE the webinar to pre-create all sequences.
During the webinar, just show the Salesforge dashboard with 50 sequences in DRAFT.

Usage: python3 launch-50-campaigns.py --key YOUR_API_KEY --workspace WORKSPACE_ID
"""

import os
import re
import json
import time
import requests
import argparse
import csv

BASE = "https://multichannel-api.salesforge.ai/public/multichannel"
CORE = "https://api.salesforge.ai/public/v2"
DELAY = 2  # seconds between API calls

def api(method, url, headers, data=None):
    for attempt in range(3):
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                r = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "PATCH":
                r = requests.patch(url, headers=headers, json=data, timeout=30)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f" [429, waiting {wait}s]", end="", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json() if r.text else {}
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
                continue
            print(f" ERROR: {e}")
            return None
    return None


def get_last_branch(headers, wks, seq):
    data = api("GET", f"{BASE}/workspaces/{wks}/sequences/{seq}/branches?limit=100", headers)
    branches = data.get("branches", [])
    for b in branches:
        if b.get("toNodeId") is None:
            return b["id"]
    return branches[-1]["id"] if branches else None


def create_campaign(headers, wks, campaign_file, campaign_num):
    """Create one multichannel sequence from a campaign file."""

    with open(campaign_file) as f:
        content = f.read()

    # Extract campaign name from first line
    name_match = re.search(r'# Campaign (\d+) — MULTICHANNEL — (.+)', content)
    if not name_match:
        print(f"  SKIP: can't parse {campaign_file}")
        return None

    campaign_name = f"Webinar Demo {campaign_num:02d} — {name_match.group(2)}"

    # Parse steps
    steps = []
    step_blocks = re.split(r'--- STEP \d+:', content)

    for block in step_blocks[1:]:  # skip header
        lines = block.strip().split('\n')
        header = lines[0].strip()

        if 'EMAIL' in header and 'FOLLOW' not in header:
            subject = ""
            body = ""
            for line in lines[1:]:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = line.replace('Body:', '').strip()
            wait = 0 if 'Day 0' in header else 3
            steps.append({"type": "email", "subject": subject, "message": f"<p>{body}</p>", "wait": wait})

        elif 'EMAIL FOLLOW' in header:
            body = ""
            for line in lines[1:]:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = line.replace('Body:', '').strip()
            steps.append({"type": "email", "subject": subject, "message": f"<p>{body}</p>", "wait": 3})

        elif 'VIEW PROFILE' in header:
            steps.append({"type": "linkedin_view", "wait": 1})

        elif 'CONNECTION REQUEST' in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_connect", "message": msg, "wait": 1})

        elif 'LINKEDIN MESSAGE' in header and 'FOLLOW' not in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_message", "message": msg, "wait": 2})

        elif 'FOLLOW-UP' in header:
            msg = ""
            for line in lines[1:]:
                if line.startswith('Message:'):
                    msg = line.replace('Message:', '').strip()
            steps.append({"type": "linkedin_message", "message": msg, "wait": 3})

    if not steps:
        print(f"  SKIP: no steps parsed from {campaign_file}")
        return None

    # 1. Create sequence
    seq_data = api("POST", f"{BASE}/workspaces/{wks}/sequences", headers, {
        "name": campaign_name, "timezone": "America/New_York"
    })
    if not seq_data:
        return None

    seq_id = seq_data["id"]
    print(f"  Seq {seq_id} created", end="", flush=True)
    time.sleep(DELAY)

    # 2. Create nodes with branch chaining
    action_map = {"email": 3, "linkedin_view": 4, "linkedin_connect": 1, "linkedin_message": 2}

    for i, step in enumerate(steps):
        branch_id = get_last_branch(headers, wks, seq_id)
        if not branch_id:
            print(f" ERROR: no branch for step {i+1}")
            break

        action_id = action_map.get(step["type"])
        node_data = {
            "actionId": action_id,
            "branchId": branch_id,
            "waitDays": step.get("wait", 0),
        }

        if step["type"] in ("email",):
            node_data["distributionStrategy"] = "equal"
            node_data["variants"] = [{
                "isEnabled": True,
                "exposureInPercentage": 100,
                "metadata": {
                    "name": "Variant A",
                    "subject": step.get("subject", ""),
                    "message": step.get("message", "")
                }
            }]
        elif step["type"] in ("linkedin_connect", "linkedin_message"):
            node_data["distributionStrategy"] = "equal"
            node_data["variants"] = [{
                "isEnabled": True,
                "exposureInPercentage": 100,
                "metadata": {
                    "name": "Variant A",
                    "message": step.get("message", "")
                }
            }]

        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/nodes/actions", headers, node_data)
        if result:
            print(f" → step {i+1}", end="", flush=True)
        time.sleep(DELAY)

    # 3. Set schedule
    api("PUT", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/schedule", headers, {
        "timezone": "America/New_York",
        "schedule": {
            "monday": {"enabled": True, "from": 8, "to": 17},
            "tuesday": {"enabled": True, "from": 8, "to": 17},
            "wednesday": {"enabled": True, "from": 8, "to": 17},
            "thursday": {"enabled": True, "from": 8, "to": 17},
            "friday": {"enabled": True, "from": 8, "to": 17},
            "saturday": {"enabled": False, "from": 0, "to": 23},
            "sunday": {"enabled": False, "from": 0, "to": 23},
        }
    })

    # 4. Set settings
    api("PATCH", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/settings", headers, {
        "plainTextEmailsEnabled": True,
        "openTrackingEnabled": False,
        "optOutLinkEnabled": False,
        "optOutTextEnabled": False,
    })

    print(f" DONE")
    return seq_id


def main():
    parser = argparse.ArgumentParser(description="Launch 50 campaigns for webinar demo")
    parser.add_argument("--key", required=True, help="Salesforge API key")
    parser.add_argument("--workspace", required=True, help="Workspace ID")
    parser.add_argument("--limit", type=int, default=50, help="Max campaigns to create")
    parser.add_argument("--start", type=int, default=1, help="Start from campaign N")
    args = parser.parse_args()

    headers = {"Authorization": args.key, "Content-Type": "application/json", "Accept": "application/json"}
    wks = args.workspace

    # Validate
    me = api("GET", f"{CORE}/me", headers)
    if not me:
        print("ERROR: API key invalid")
        return
    print(f"Connected: {me.get('apiKeyName', 'unknown')}")

    # Find campaign files
    campaigns_dir = os.path.dirname(os.path.abspath(__file__)) + "/campaigns"
    files = sorted([f for f in os.listdir(campaigns_dir) if f.endswith('.txt')])
    files = files[args.start - 1:args.limit]

    print(f"\nCreating {len(files)} multichannel sequences...\n")

    created = []
    for i, f in enumerate(files):
        num = i + args.start
        filepath = os.path.join(campaigns_dir, f)
        print(f"[{num:02d}/{len(files)}] {f}", end="", flush=True)
        seq_id = create_campaign(headers, wks, filepath, num)
        if seq_id:
            created.append({"file": f, "sequence_id": seq_id})
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"DONE: {len(created)}/{len(files)} sequences created in DRAFT")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
