"""
NeutronIndex — Vast.ai GPU Marketplace Scraper
Fetches individual machine offers with specs, reliability, and location.
"""
import httpx
from datetime import datetime, timezone

VASTAI_SEARCH = "https://console.vast.ai/api/v0/bundles/"


async def fetch_vastai(gpu_name: str = None, limit: int = 500) -> list[dict]:
    """Fetch GPU offers from Vast.ai marketplace."""
    now = datetime.now(timezone.utc).isoformat()
    records = []

    params = {
        "q": json.dumps({
            "verified": {"eq": True},
            "external": {"eq": False},
            "rentable": {"eq": True},
            "rented": {"eq": False},
            "type": "on-demand",
            "limit": limit,
            "order": [["dph_total", "asc"]],
        })
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(VASTAI_SEARCH, params=params)
        resp.raise_for_status()
        data = resp.json()

    for offer in data.get("offers", []):
        gpu_model = offer.get("gpu_name", "").upper().replace(" ", "_")
        if gpu_name and gpu_name.lower() not in gpu_model.lower():
            continue

        records.append({
            "timestamp": now,
            "provider": "vastai",
            "gpu_model": gpu_model,
            "gpu_count": offer.get("num_gpus", 1),
            "region": offer.get("geolocation", "unknown"),
            "price_per_hour_usd": offer.get("dph_total", 0),
            "pricing_type": "bid",
            "available": True,
            "vcpus": offer.get("cpu_cores_effective", 0),
            "ram_gb": round(offer.get("cpu_ram", 0) / 1024, 1),
            "vram_gb": round(offer.get("gpu_totalram", 0) / 1024, 1),
            "interconnect": "pcie",
            "reliability_score": offer.get("reliability2", None),
            "machine_id": offer.get("id"),
        })

    return records
