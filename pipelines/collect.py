"""
NeutronIndex — Main Collection Pipeline
Orchestrates scraping, enrichment, and export.
Run hourly via Cloudflare Worker cron or GitHub Actions.
"""
import asyncio
import json
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from pipelines.scrapers.shadeform import fetch_all_providers
from pipelines.scrapers.runpod import fetch_runpod
from pipelines.scrapers.vastai import fetch_vastai
from pipelines.energy.fetcher import fetch_carbon_intensity, resolve_zone
from pipelines.enrich import enrich_basic_tco


async def collect(
    providers: str = "all",
    enrich_energy: bool = False,
    output_dir: str = "exports",
    em_api_key: str = None,
):
    """Run full collection cycle."""
    all_records = []

    # 1. Fetch GPU pricing
    if providers in ("all", "shadeform"):
        records = await fetch_all_providers()
        all_records.extend(records)
        print(f"[shadeform] {len(records)} records")

    if providers in ("all", "runpod"):
        records = await fetch_runpod()
        all_records.extend(records)
        print(f"[runpod] {len(records)} records")

    if providers in ("all", "vastai"):
        records = await fetch_vastai(limit=200)
        all_records.extend(records)
        print(f"[vastai] {len(records)} records")

    # 2. Enrich with energy/carbon data
    if enrich_energy:
        zones_cache = {}
        for record in all_records:
            zone = resolve_zone(record.get("region", ""))
            if zone and zone not in zones_cache:
                carbon = await fetch_carbon_intensity(zone, em_api_key)
                zones_cache[zone] = carbon
            carbon_data = zones_cache.get(zone)
            enrich_basic_tco(record, carbon_data)
    else:
        for record in all_records:
            enrich_basic_tco(record)

    # 3. Export
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # JSON
    json_path = Path(output_dir) / "latest.json"
    with open(json_path, "w") as f:
        json.dump({"generated": ts, "count": len(all_records), "records": all_records}, f, indent=2)

    # CSV
    csv_path = Path(output_dir) / "latest.csv"
    if all_records:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_records[0].keys())
            writer.writeheader()
            writer.writerows(all_records)

    print(f"\n[export] {len(all_records)} records -> {output_dir}/ ({ts})")
    return all_records


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NeutronIndex Collector")
    parser.add_argument("--providers", default="all")
    parser.add_argument("--enrich-energy", action="store_true")
    parser.add_argument("--output", default="exports")
    parser.add_argument("--em-api-key", default=None)
    args = parser.parse_args()

    asyncio.run(collect(args.providers, args.enrich_energy, args.output, args.em_api_key))
