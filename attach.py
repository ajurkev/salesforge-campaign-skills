"""
Attach sender profiles and enroll contacts to ALL sequences in a workspace.
Run after launch-50-campaigns.py finishes.

Usage: python3 attach-senders-enroll.py --key KEY --workspace WKS_ID --sender-profile-id 5830
"""

import argparse
import json
import time
import requests

BASE = "https://multichannel-api.salesforge.ai/public/multichannel"
CORE = "https://api.salesforge.ai/public/v2"
DELAY = 1.5


def api(method, url, headers, data=None):
    for attempt in range(3):
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 429:
                time.sleep(10 * (attempt + 1))
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--sender-profile-id", type=int, required=True)
    parser.add_argument("--tag", default="webinar-live", help="Contact tag to enroll")
    args = parser.parse_args()

    headers = {"Authorization": args.key, "Content-Type": "application/json", "Accept": "application/json"}
    wks = args.workspace

    # 1. Get all contacts with tag
    print("Fetching contacts...")
    contacts = []
    offset = 0
    while True:
        data = api("GET", f"{CORE}/workspaces/{wks}/contacts?limit=100&offset={offset}", headers)
        if not data or not data.get("data"):
            break
        contacts.extend(data["data"])
        if len(data["data"]) < 100:
            break
        offset += 100

    # Filter by tag
    tagged = [c for c in contacts if args.tag in (c.get("tags") or [])]
    lead_ids = [c["id"] for c in tagged]
    print(f"Found {len(lead_ids)} contacts with tag '{args.tag}'")

    if not lead_ids:
        # Use all contacts if no tag match
        lead_ids = [c["id"] for c in contacts]
        print(f"Using all {len(lead_ids)} contacts instead")

    # 2. Get all sequences (draft)
    print("\nFetching sequences...")
    all_sequences = []
    page = 1
    while True:
        data = api("GET", f"{BASE}/workspaces/{wks}/sequences?page={page}&limit=100&status=draft", headers)
        if not data:
            break
        seqs = data.get("sequences", data.get("data", []))
        if not seqs:
            break
        all_sequences.extend(seqs)
        pagination = data.get("pagination", {})
        if not pagination.get("hasNext", False):
            break
        page += 1

    # Filter to webinar demo sequences
    demo_seqs = [s for s in all_sequences if "Webinar Demo" in s.get("name", "")]
    print(f"Found {len(demo_seqs)} webinar demo sequences in DRAFT")

    # 3. Attach sender + enroll contacts to each
    success = 0
    for seq in demo_seqs:
        seq_id = seq["id"]
        name = seq.get("name", "")
        print(f"  [{seq_id}] {name[:50]}...", end="", flush=True)

        # Attach sender
        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/sender-profiles", headers, {
            "senderProfileIds": [args.sender_profile_id]
        })
        if result:
            print(f" sender OK", end="", flush=True)
        time.sleep(DELAY)

        # Enroll contacts
        result = api("POST", f"{BASE}/workspaces/{wks}/sequences/{seq_id}/enrollments", headers, {
            "filters": {"leadIds": lead_ids},
            "limit": len(lead_ids)
        })
        if result:
            enrolled = len(result.get("leadIds", []))
            print(f" enrolled {enrolled}", end="", flush=True)
            success += 1
        time.sleep(DELAY)

        print(" DONE")

    print(f"\n{'='*60}")
    print(f"DONE: {success}/{len(demo_seqs)} sequences — senders attached + contacts enrolled")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
