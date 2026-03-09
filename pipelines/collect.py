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


async def collect(
    providers="all",
    output_dir="exports",
):
    all_records = []

    if providers in ("all", "shadeform"):
        try:
            records = await fetch_all_providers()
            all_records.extend(records)
            print(f"[shadeform] {len(records)} records")
        except Exception as e:
            print(f"[shadeform] FAILED: {e}")

    if providers in ("all", "runpod"):
        try:
            records = await fetch_runpod()
            all_records.extend(records)
            print(f"[runpod] {len(records)} records")
        except Exception as e:
            print(f"[runpod] FAILED: {e}")

    if providers in ("all", "vastai"):
        try:
            from pipelines.scrapers.vastai import fetch_vastai
            records = await fetch_vastai(limit=200)
            all_records.extend(records)
            print(f"[vastai] {len(records)} records")
        except Exception as e:
            print(f"[vastai] SKIPPED: {e}")

    if not all_records:
        print("No data collected!")
        sys.exit(1)

    for record in all_records:
        enrich_basic_tco(record)

    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    with open(Path(output_dir) / "latest.json", "w") as f:
        json.dump({"generated": ts, "count": len(all_records), "records": all_records}, f, indent=2)

    if all_records:
        with open(Path(output_dir) / "latest.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_records[0].keys())
            writer.writeheader()
            writer.writerows(all_records)

    print(f"\n[export] {len(all_records)} records -> {output_dir}/ ({ts})")


if __name__ == "__main__":
    asyncio.run(collect())
