# NeutronIndex — Live Multi-Cloud AI Compute Pricing & True TCO Index

[![Hourly Update](https://img.shields.io/badge/updates-hourly-brightgreen)]()
[![Providers](https://img.shields.io/badge/providers-25%2B-blue)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-orange)]()

> The complete "true cost per FLOP" for AI workloads — GPU pricing, spot availability, energy cost, and carbon intensity across 25+ cloud providers, updated hourly.

## What Is NeutronIndex?

NeutronIndex is an **open-core dataset and API** that answers the question enterprises actually need answered:

> *"What does it REALLY cost to run this AI workload — including power, carbon, and regional variance?"*

Raw GPU pricing is only ~60% of true compute cost. NeutronIndex normalizes across providers and layers in:
- ⚡ Regional electricity pricing ($/kWh by datacenter zone)
- 🌱 Carbon intensity (gCO2eq/kWh, Scope 2/3 aligned)
- 🔥 Spot vs on-demand vs reserved pricing with availability signals
- 📊 True TCO per FLOP, per token, per training run

## Data Sources (All Public)

| Source | Data | Frequency |
|--------|------|-----------|
| Shadeform API | GPU pricing across 21+ providers | Hourly |
| RunPod API | Community + secure cloud pricing | Hourly |
| Vast.ai API | Machine-level offers + reliability | Hourly |
| AWS/Azure/GCP | Direct instance pricing | Hourly |
| Electricity Maps | Carbon intensity by zone | Hourly |
| WattTime | Marginal emissions data | Hourly |
| EIA / ENTSO-E | Regional electricity pricing | Daily |

## Schema

All exports follow the [NeutronIndex Schema v1](schemas/schema_v1.json):

```json
{
  "timestamp": "2026-03-08T20:00:00Z",
  "provider": "lambda",
  "gpu_model": "H100_SXM",
  "gpu_count": 8,
  "region": "us-east-1",
  "price_per_hour_usd": 23.84,
  "pricing_type": "on_demand",
  "available": true,
  "vcpus": 208,
  "ram_gb": 1024,
  "vram_gb": 640,
  "interconnect": "nvlink",
  "electricity_price_kwh": 0.087,
  "carbon_intensity_gco2_kwh": 372.1,
  "tdp_watts": 5600,
  "energy_cost_per_hour_usd": 0.487,
  "tco_per_hour_usd": 24.327,
  "tco_per_pflop_usd": 0.0121,
  "carbon_per_hour_gco2": 2083.76,
  "neutron_score": null
}
```

> **Note:** `neutron_score` (the proprietary composite TCO+efficiency+carbon score) is available in the [paid API/dataset](https://aws.amazon.com/marketplace).

## Exports

| Format | Location | Access |
|--------|----------|--------|
| CSV | `exports/latest.csv` | Free (this repo) |
| Parquet | `exports/latest.parquet` | Free (this repo) |
| JSON API | `api.neutronindex.com/v1/` | Free tier (100 req/day) |
| Full History + Score | AWS Data Exchange | Paid subscription |

## Methodology

Full methodology is documented in [docs/methodology.md](docs/methodology.md). All source code for data collection is open. The proprietary TCO normalization engine and NeutronScore algorithm are closed-source but the inputs and methodology principles are fully disclosed.

## Quick Start

```bash
# Clone and install
git clone https://github.com/alpha-one-index/neutron-index.git
cd neutron-index
pip install -r requirements.txt

# Run a single collection cycle
python -m pipelines.collect --providers all --output exports/

# Run with energy/carbon enrichment
python -m pipelines.collect --enrich-energy --output exports/
```

## License

Data collection pipelines: **Apache 2.0** (use freely)
NeutronIndex dataset exports: **CC BY 4.0** (cite us)
NeutronScore engine: **Proprietary** (available via paid API/AWS DX)

---

*Part of the [Alpha One Index](https://alphaoneindex.com) ecosystem — AI Infrastructure & Security Research Hub*
