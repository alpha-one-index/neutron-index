"""
NeutronIndex — Shadeform GPU Pricing Scraper
Fetches live GPU pricing from 21+ providers via Shadeform aggregator API.
No API key required for basic queries.
"""
import httpx
import json
from datetime import datetime, timezone
from typing import Optional

SHADEFORM_BASE = "https://api.shadeform.ai/v1/instances/types"

PROVIDER_MAP = {
    "aws": "aws",
    "azure": "azure", 
    "gcp": "gcp",
    "lambdalabs": "lambda",
    "paperspace": "paperspace",
    "coreweave": "coreweave",
    "crusoe": "crusoe",
    "nebius": "nebius",
    "vultr": "vultr",
    "hyperstack": "hyperstack",
    "digitalocean": "digitalocean",
    "scaleway": "scaleway",
    "fluidstack": "fluidstack",
    "tensordock": "tensordock",
    "oblivus": "oblivus",
    "datacrunch": "datacrunch",
    "latitude": "latitude",
    "jarvislabs": "jarvislabs",
    "massed_compute": "massed_compute",
}

GPU_MODEL_NORMALIZE = {
    "A100": "A100_SXM",
    "A100_PCIE": "A100_PCIe",
    "A100 80GB": "A100_SXM",
    "H100": "H100_SXM",
    "H100_PCIE": "H100_PCIe",
    "H100 80GB SXM": "H100_SXM",
    "H200": "H200_SXM",
    "L40S": "L40S",
    "A10G": "A10G",
    "RTX 4090": "RTX_4090",
    "RTX 6000 Ada": "RTX_6000_Ada",
    "B200": "B200",
    "MI300X": "MI300X",
}


def normalize_gpu_model(raw_name: str) -> str:
    for key, val in GPU_MODEL_NORMALIZE.items():
        if key.lower() in raw_name.lower():
            return val
    return raw_name.upper().replace(" ", "_")


async def fetch_shadeform(
    gpu_filter: Optional[str] = None,
    api_key: Optional[str] = None,
) -> list[dict]:
    """Fetch GPU instance types from Shadeform."""
    headers = {}
    if api_key:
        headers["X-API-KEY"] = api_key

    params = {}
    if gpu_filter:
        params["gpu_type"] = gpu_filter

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SHADEFORM_BASE, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    now = datetime.now(timezone.utc).isoformat()
    records = []

    for instance in data.get("instance_types", []):
        cloud = instance.get("cloud", "unknown").lower()
        provider = PROVIDER_MAP.get(cloud, cloud)

        gpu_info = instance.get("gpu", {})
        gpu_model = normalize_gpu_model(gpu_info.get("name", "unknown"))
        gpu_count = gpu_info.get("count", 1)

        record = {
            "timestamp": now,
            "provider": provider,
            "gpu_model": gpu_model,
            "gpu_count": gpu_count,
            "region": instance.get("region", "unknown"),
            "price_per_hour_usd": instance.get("hourly_price", 0) / 100,  # cents -> dollars
            "pricing_type": "on_demand",
            "available": instance.get("available", False),
            "vcpus": instance.get("vcpus", 0),
            "ram_gb": instance.get("memory", 0) / 1024,  # MB -> GB
            "vram_gb": gpu_info.get("memory", 0),
            "interconnect": gpu_info.get("interconnect"),
            # Energy fields populated by enrichment pipeline
            "electricity_price_kwh": None,
            "carbon_intensity_gco2_kwh": None,
            "tdp_watts": None,
            "energy_cost_per_hour_usd": None,
            "tco_per_hour_usd": None,
            "tco_per_pflop_usd": None,
            "carbon_per_hour_gco2": None,
            "neutron_score": None,  # PRIVATE — computed in private repo
        }
        records.append(record)

    return records


async def fetch_all_providers() -> list[dict]:
    """Fetch from all providers via Shadeform."""
    return await fetch_shadeform()
