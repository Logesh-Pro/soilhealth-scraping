# Tamil Nadu Soil Health Card Data Extraction

## Purpose

This repository contains a web-data extraction and preprocessing pipeline for publicly accessible Soil Health Card portal data, focused on Tamil Nadu and the Soil Health Card RKVY scheme for cycle 2026-27.

## Dataset

The main ML-ready dataset is:

`tn_rkvy_village_ml_ready.csv`

Current coverage:

- 744 unique village-level records
- 124 blocks
- 30 districts
- Cycle: 2026-27
- Scheme: Soil Health Card RKVY

The village records contain aggregate classifications for:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Organic Carbon (OC)
- pH
- Electrical Conductivity (EC)
- Sulfur (S)
- Iron (Fe)
- Zinc (Zn)
- Copper (Cu)
- Boron (B)
- Manganese (Mn)

The processed dataset also contains category percentages, sample counts, parameter coverage, dominant categories, and data-quality indicators.

## Important interpretation

These 744 records are village-level aggregate Soil Health Card statistics returned by the public portal.

They are not individual farmer-level numeric soil-test measurements.

Therefore, they should be treated as contextual/background soil-health features rather than as a statewide dataset of raw laboratory measurements.

## Numeric SHC report parser

The repository also contains a parser for an authorized individual Soil Health Card HTML report.

The parser can extract numeric:

- N (kg/ha)
- P (kg/ha)
- K (kg/ha)
- Organic Carbon (%)
- pH
- EC (dS/m)
- Sulfur (ppm)
- Fe (ppm)
- Zn (ppm)
- Cu (ppm)
- B (ppm)
- Mn (ppm)

This parser was validated against one completed Soil Health Card report.

The individual example report is intentionally excluded from Git because it contains identifying/location information.

## Main files

### Dataset

- `tn_rkvy_village_records.csv` — raw village-level extracted records
- `tn_rkvy_village_records.json` — raw village-level JSON
- `tn_rkvy_village_ml_ready.csv` — processed ML-ready dataset
- `tn_rkvy_village_baseline.csv` — intermediate baseline dataset

### Extraction scripts

- `tn_rkvy_scan.py` — Tamil Nadu district-level scan
- `tn_rkvy_block_scan.py` — block-level discovery
- `tn_rkvy_village_scan.py` — village-level extraction
- `tn_rkvy_village_baseline.py` — baseline feature generation
- `tn_rkvy_ml_ready.py` — ML feature preparation

### SHC report parsing

- `parse_shc_reports.py` — numeric SHC HTML parser
- `clean_numeric_shc.py` — numeric dataset cleanup
- `validate_numeric_shc.py` — numeric dataset validation
- `parse_soil_report.py` — initial report parser

### Geography / intermediate datasets

- `tn_districts.json`
- `tn_rkvy_block_records.csv`
- `tn_rkvy_block_records.json`
- `tn_rkvy_district_nutrients.csv`
- `tn_rkvy_district_aggregated.csv`

## Data-quality notes

Of the 744 village records:

- 721 have complete parameter coverage
- 17 have minor missing parameter coverage
- 6 have partial coverage

Parameter sample counts are preserved separately because some villages have fewer observations for particular nutrients.

## ML handoff

Recommended primary input:

`tn_rkvy_village_ml_ready.csv`

Use `village_id` as the village identifier rather than village name alone because village names are not globally unique.

Potential feature groups include:

- geographic context
- N/P/K category distributions
- organic-carbon distribution
- pH distribution
- salinity distribution
- micronutrient deficiency rates
- sample counts
- parameter completeness

## Future integration

This repository does not currently contain the project's IoT sensor dataset.

The intended future integration can combine this Government baseline with authorized numeric SHC measurements and project-specific IoT observations.

## Responsible-use note

Individual SHC reports may contain personal or location information. Raw individual reports and derived files containing identifying information are excluded from this repository.

Automated collection of individual farmer reports should not be performed where prohibited by the portal's access controls or terms.

