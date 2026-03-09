"""
NeutronIndex — Energy & Carbon Data Fetcher
Fetches carbon intensity and electricity data from public APIs.

IMPORTANT: Electricity Maps free tier is limited to 1 zone.
For production multi-zone coverage, use commercial tier or
supplement with WattTime + EIA data.
"""
import httpx
from datetime import datetime, timezone
from typing import Optional

ELECTRICITYMAPS_BASE = "https://api.electricitymap.org/v3"
WATTTIME_BASE = "https://api.watttime.org/v3"

# Mapping of cloud provider regions to Electricity Maps zones
REGION_TO_ZONE = {
    "us-east-1": "US-MIDA-PJM",
    "us-east-2": "US-MIDA-PJM",
    "us-west-1": "US-CAL-CISO",
    "us-west-2": "US-NW-PACW",
    "eu-west-1": "IE",
    "eu-west-2": "GB",
    "eu-central-1": "DE",
    "ap-northeast-1": "JP-TK",
    "ap-southeast-1": "SG",
    "ap-south-1": "IN-WE",
    "ca-central-1": "CA-ON",
    "sa-east-1": "BR-CS",
    "me-south-1": "BH",
    "af-south-1": "ZA",
    "europe-west1": "BE",
    "europe-west4": "NL",
    "northeurope": "IE",
    "westeurope": "NL",
    "eastus": "US-MIDA-PJM",
    "westus": "US-CAL-CISO",
    "westus2": "US-NW-PACW",
}


async def fetch_carbon_intensity(
    zone: str,
    em_api_key: Optional[str] = None,
) -> Optional[dict]:
    """Fetch latest carbon intensity from Electricity Maps."""
    headers = {}
    if em_api_key:
        headers["auth-token"] = em_api_key

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{ELECTRICITYMAPS_BASE}/carbon-intensity/latest",
                params={"zone": zone},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "zone": zone,
                "carbon_intensity_gco2_kwh": data.get("carbonIntensity"),
                "datetime": data.get("datetime"),
                "estimation_method": data.get("estimationMethod"),
            }
        except Exception:
            return None


async def fetch_watttime_intensity(
    latitude: float,
    longitude: float,
    wt_token: str,
) -> Optional[dict]:
    """Fetch marginal emissions from WattTime (requires auth)."""
    headers = {"Authorization": f"Bearer {wt_token}"}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"{WATTTIME_BASE}/signal-index",
                params={"latitude": latitude, "longitude": longitude},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "latitude": latitude,
                "longitude": longitude,
                "moer": data.get("data", [{}])[0].get("value"),
                "frequency": data.get("meta", {}).get("data_point_period_seconds"),
            }
        except Exception:
            return None


def resolve_zone(cloud_region: str) -> Optional[str]:
    """Map a cloud provider region to an Electricity Maps zone."""
    return REGION_TO_ZONE.get(cloud_region)
