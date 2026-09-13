# Data Dictionary

This folder contains the point-level inputs used in the analysis pipeline.

## `blm_pei_2023_points.csv`

| Column | Meaning | Unit | Source |
| --- | --- | --- | --- |
| `point_id` | Unique identifier for each monitoring point | None | Derived in this repository |
| `easting` | Projected x coordinate for the point | meters | BLM PEI source and/or cleaned GIS extract |
| `northing` | Projected y coordinate for the point | meters | BLM PEI source and/or cleaned GIS extract |
| `longitude` | Geographic longitude | degrees | Converted from projected coordinates |
| `latitude` | Geographic latitude | degrees | Converted from projected coordinates |
| `debris_measured` | Debris inspection value recorded at the point | see source report | BLM 2023 Post-Event Inspection report |
| `debris_unit` | Unit associated with the debris measurement | reported unit | BLM 2023 Post-Event Inspection report |
| `category` | Point category used in downstream analysis | categorical | Derived / harmonized in this repository |
| `source_notes` | Any extraction or correction notes | text | Derived in this repository |

## `control_points.csv`

| Column | Meaning | Unit | Source |
| --- | --- | --- | --- |
| `point_id` | Unique identifier for the candidate control point | None | Derived in this repository |
| `easting` | Projected x coordinate for the point | meters | GIS selection / manual curation |
| `northing` | Projected y coordinate for the point | meters | GIS selection / manual curation |
| `longitude` | Geographic longitude | degrees | Converted from projected coordinates |
| `latitude` | Geographic latitude | degrees | Converted from projected coordinates |
| `is_valid` | Flag indicating whether the candidate passed validation | boolean | Manual validation in this repository |
| `validation_notes` | Reason the point was accepted or rejected | text | Derived in this repository |
