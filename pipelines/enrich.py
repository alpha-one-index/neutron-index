"""
NeutronIndex — Public TCO Enrichment (Basic)
Adds energy cost and carbon data to raw GPU pricing records.
This is the open-source baseline. The proprietary NeutronScore
and advanced normalization live in the private repo.
"""
from pipelines.scrapers.gpu_specs import GPU_SPECS, PROVIDER_PUE


def enrich_basic_tco(record: dict, carbon_data: dict = None) -> dict:
    """Add basic energy cost and carbon to a pricing record."""
    gpu_model = record.get("gpu_model", "")
    provider = record.get("provider", "")
    gpu_count = record.get("gpu_count", 1)

    spec = GPU_SPECS.get(gpu_model)
    if not spec:
        return record

    pue = PROVIDER_PUE.get(provider, PROVIDER_PUE["default"])
    tdp_per_gpu = spec["tdp_watts"]
    total_tdp = tdp_per_gpu * gpu_count
    total_power_w = total_tdp * pue
    total_power_kw = total_power_w / 1000

    # Energy cost (use provided electricity price or default)
    elec_price = record.get("electricity_price_kwh") or 0.10  # $/kWh default
    energy_cost_hour = total_power_kw * elec_price

    # Total cost
    gpu_price = record.get("price_per_hour_usd", 0)
    tco_hour = gpu_price + energy_cost_hour

    # Cost per PFLOP
    fp16_tflops = spec.get("fp16_tflops", 0) * gpu_count
    fp16_pflops = fp16_tflops / 1000
    tco_per_pflop = tco_hour / fp16_pflops if fp16_pflops > 0 else None

    # Carbon
    carbon_intensity = None
    carbon_per_hour = None
    if carbon_data:
        carbon_intensity = carbon_data.get("carbon_intensity_gco2_kwh")
        if carbon_intensity:
            carbon_per_hour = total_power_kw * carbon_intensity

    record.update({
        "tdp_watts": total_tdp,
        "energy_cost_per_hour_usd": round(energy_cost_hour, 4),
        "tco_per_hour_usd": round(tco_hour, 4),
        "tco_per_pflop_usd": round(tco_per_pflop, 6) if tco_per_pflop else None,
        "carbon_intensity_gco2_kwh": carbon_intensity,
        "carbon_per_hour_gco2": round(carbon_per_hour, 2) if carbon_per_hour else None,
        "electricity_price_kwh": elec_price,
    })

    return record
