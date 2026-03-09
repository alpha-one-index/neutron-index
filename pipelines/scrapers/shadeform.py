"""NeutronIndex - Shadeform Scraper"""
import httpx
import os
from datetime import datetime, timezone

SHADEFORM_BASE = "https://api.shadeform.ai/v1/instances/types"


async def fetch_all_providers() -> list[dict]:
    api_key = os.environ.get("SHADEFORM_API_KEY", "")
    headers = {"X-API-KEY": api_key} if api_key else {}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SHADEFORM_BASE, headers=headers, params={"sort": "price"})
        resp.raise_for_status()
        data = resp.json()

    now = datetime.now(timezone.utc).isoformat()
    records = []

    for inst in data.get("instance_types", []):
        cfg = inst.get("configuration", {})
        gpu_type = cfg.get("gpu_type", "unknown")
        num_gpus = cfg.get("num_gpus", 1)
        vram = cfg.get("vram_per_gpu_in_gb", 0)
        price_cents = inst.get("hourly_price", 0)

        for avail in inst.get("availability", []):
            records.append({
                "timestamp": now,
                "provider": inst.get("cloud", "unknown"),
                "gpu_model": gpu_type,
                "gpu_count": num_gpus,
                "region": avail.get("region", "unknown"),
                "price_per_hour_usd": round(price_cents / 100, 4),
                "pricing_type": "on_demand",
                "available": avail.get("available", False),
                "vcpus": cfg.get("vcpus", 0),
                "ram_gb": cfg.get("memory_in_gb", 0),
                "vram_gb": vram,
                "interconnect": "nvlink" if cfg.get("num_gpus", 1) > 1 else "pcie",
                "shade_instance_type": inst.get("shade_instance_type", ""),
            })

    return records
