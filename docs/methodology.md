# NeutronIndex Methodology

## Data Collection

NeutronIndex collects GPU compute pricing from 25+ cloud providers every hour using:
1. **Shadeform API** — Aggregated pricing from 21 providers (no API key required)
2. **RunPod GraphQL API** — Secure, community, and spot pricing
3. **Vast.ai REST API** — Individual machine offers with reliability scores
4. **Direct provider pages** — AWS, Azure, GCP pricing endpoints

## TCO Calculation

True Cost of Ownership goes beyond the listed GPU rental price:

```
TCO/hr = GPU_price/hr + Energy_cost/hr

Where:
  Energy_cost/hr = (GPU_TDP × GPU_count × PUE) / 1000 × Electricity_price_kWh

  TCO/PFLOP = TCO/hr ÷ (FP16_TFLOPS × GPU_count / 1000)

  Carbon/hr = (GPU_TDP × GPU_count × PUE) / 1000 × Carbon_intensity_gCO2/kWh
```

### Key Variables
- **TDP**: Thermal Design Power from vendor datasheets
- **PUE**: Power Usage Effectiveness (datacenter efficiency ratio, >1.0)
- **Electricity price**: Regional grid price from EIA/ENTSO-E data
- **Carbon intensity**: gCO2eq per kWh from Electricity Maps / WattTime

## NeutronScore (Proprietary)

The NeutronScore is a composite 0–100 rating that normalizes TCO, availability,
reliability, carbon impact, and value-per-FLOP into a single decision metric.

The scoring algorithm is proprietary and available only through paid subscriptions
(AWS Data Exchange or API Pro/Enterprise tiers). The inputs are fully disclosed above.

## Update Frequency
- GPU pricing: Hourly
- Carbon intensity: Hourly
- Electricity pricing: Daily (grid data publication lag)
- NeutronScore: Hourly (recomputed with each pricing update)

## Disclosure
NeutronIndex is editorially independent. We have no financial relationships with
any cloud provider. All data sources are public. Methodology changes are versioned
and documented in this repository.
