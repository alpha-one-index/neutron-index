"""NeutronIndex - Main Collection Pipeline"""
import asyncio
import json
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from pipelines.scrapers.shadeform import fetch_all_providers
from pipelines.scrapers.runpod import fetch_runpod
from pipelines.enrich import enrich_basic_tco


async def collect():
    all_records = []

    try:
        records = await fetch_all_providers()
        all_records.extend(records)
        print(f"[shadeform] {len(records)} records")
    except Exception as e:
        print(f"[shadeform] FAILED: {e}")

    try:
        records = await fetch_runpod()
        all_records.extend(records)
        print(f"[runpod] {len(records)} records")
    except Exception as e:
        print(f"[runpod] FAILED: {e}")

    if not all_records:
        print("No data collected!")
        sys.exit(1)

    for record in all_records:
        enrich_basic_tco(record)

    os.makedirs("exports", exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    with open("exports/latest.json", "w") as f:
        json.dump({"generated": ts, "count": len(all_records), "records": all_records}, f, indent=2)

    if all_records:
        all_keys = []
        seen = set()
        for r in all_records:
            for k in r.keys():
                if k not in seen:
                    all_keys.append(k)
                    seen.add(k)
        with open("exports/latest.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore", restval="")
            writer.writeheader()
            writer.writerows(all_records)

    print(f"[export] {len(all_records)} records exported ({ts})")


if __name__ == "__main__":
    asyncio.run(collect())
