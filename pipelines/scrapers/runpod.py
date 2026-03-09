"""
NeutronIndex — RunPod GPU Pricing Scraper
Fetches community cloud, secure cloud, and spot pricing from RunPod.
"""
import httpx
from datetime import datetime, timezone

RUNPOD_GRAPHQL = "https://api.runpod.io/graphql"

QUERY_GPU_TYPES = """
query GpuTypes {
    gpuTypes {
        id
        displayName
        memoryInGb
        secureCloud
        communityCloud
        lowestPrice(input: { gpuCount: 1 }) {
            minimumBidPrice
            uninterruptablePrice
            minVcpu
            minMemory
        }
        securePrice
        communityPrice
        secureSpotPrice
        communitySpotPrice
    }
}
"""


async def fetch_runpod() -> list[dict]:
    """Fetch GPU pricing from RunPod GraphQL API."""
    now = datetime.now(timezone.utc).isoformat()
    records = []

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            RUNPOD_GRAPHQL,
            json={"query": QUERY_GPU_TYPES},
        )
        resp.raise_for_status()
        data = resp.json()

    for gpu in data.get("data", {}).get("gpuTypes", []):
        base = {
            "timestamp": now,
            "provider": "runpod",
            "gpu_model": gpu.get("displayName", "").upper().replace(" ", "_"),
            "gpu_count": 1,
            "region": "us",  # RunPod doesn't expose per-region in this query
            "vram_gb": gpu.get("memoryInGb", 0),
        }

        # Secure cloud on-demand
        if gpu.get("securePrice"):
            records.append({
                **base,
                "price_per_hour_usd": gpu["securePrice"],
                "pricing_type": "on_demand",
                "available": gpu.get("secureCloud", False),
            })

        # Community cloud
        if gpu.get("communityPrice"):
            records.append({
                **base,
                "price_per_hour_usd": gpu["communityPrice"],
                "pricing_type": "community",
                "available": gpu.get("communityCloud", False),
            })

        # Spot pricing
        if gpu.get("secureSpotPrice"):
            records.append({
                **base,
                "price_per_hour_usd": gpu["secureSpotPrice"],
                "pricing_type": "spot",
                "available": gpu.get("secureCloud", False),
            })

    return records
