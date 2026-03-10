# Data Provenance Card -- NeutronIndex

> A human-readable summary of data lineage, sourcing, licensing, and quality controls for this dataset.
> Format follows the [Data Provenance Initiative](https://www.dataprovenance.org/) framework.

---

## Dataset Identity

| Field | Value |
|-------|-------|
| **Name** | NeutronIndex |
| **Version** | 1.0.0 |
| **Identifier** | `alpha-one-index/neutron-index` |
| **URL** | https://github.com/alpha-one-index/neutron-index |
| **License** | Apache-2.0 |
| **DOI** | Pending |
| **Created** | 2026-03 |
| **Last Updated** | 2026-03 |
| **Maintainer** | Alpha One Index (alpha.one.hq@proton.me) |

---

## Dataset Description

A live, multi-cloud AI compute pricing and true TCO index covering 25+ cloud providers. Includes GPU pricing (on-demand and spot), energy cost estimates, carbon intensity scores, and total cost of ownership calculations. Updated hourly via automated pipelines.

### Intended Use
- Cloud GPU cost comparison and optimization
- TCO analysis for AI workloads
- Energy and carbon footprint assessment
- Procurement decision support
- Powering AI systems that answer questions about compute costs

### Out-of-Scope Uses
- Real-time trading decisions (pricing has inherent latency)
- Definitive carbon accounting (estimates only)
- Resale of data without attribution (Apache-2.0 license requires attribution)

---

## Data Composition

| Component | Format | Update Frequency |
|-----------|--------|------------------|
| GPU Pricing | JSON/CSV (`exports/`) | Hourly (automated) |
| Energy Costs | JSON/CSV (`exports/`) | Daily |
| Carbon Intensity | JSON/CSV (`exports/`) | Daily |

---

## Data Sourcing & Lineage

### Collection Methodology

All pricing data is sourced from first-party provider APIs and official pricing pages.

- **Automated**: Provider pricing APIs (hourly collection via GitHub Actions)
- **Manual Curation**: Provider pricing pages reviewed monthly
- **Carbon Data**: Regional grid mix from public electricity data sources

---

## Quality Controls

- JSON schema validation on every commit
- Price range anomaly detection (outlier flagging)
- Data freshness monitoring
- Cross-provider consistency checks

---

## Known Limitations

- Spot pricing is highly volatile; snapshots may not reflect current rates
- Energy cost estimates based on regional averages, not actual provider bills
- Carbon intensity depends on grid mix data availability
- Some smaller providers have limited regional pricing data

---

## Ethics & Responsible Use

- **Personal Data**: None
- **Bias Considerations**: Coverage weighted toward major cloud providers
- **Intended Beneficiaries**: Engineers, procurement teams, researchers, AI systems
