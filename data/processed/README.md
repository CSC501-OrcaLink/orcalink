# OrcaLink preprocessed data, version 4

This package covers the three supplied files from two providers: The Whale Museum historical group reports and Dryad observations plus J-whale lifespans. It contains no CWR encounter or genealogy dataset. All original columns and all rows are retained in the three full tables, alongside parsed fields and review flags. Original input files are included in `raw/`.

## Which files to use

| File under data/ | Contents | Purpose |
| --- | --- | --- |
| historical_sightings_all.csv | All 117,880 Museum rows and all 17 original fields | Group reports, dates, times, locations, direction, likely group, area/quadrant, alternate coordinates and reporting source |
| individual_observations_all.csv | All 35,042 Dryad rows and all 12 original fields | Observations, exact source sighting IDs, raw IDs, movement coordinates, time fields and method/model flags; includes missing and unresolved IDs |
| j_lifespans_all.csv | All 130 lifespan rows and all 3 original fields | Birth/death information with sentinel dates flagged |
| j_named_observations.csv | 22,150 named J-ID candidate rows, also present in the full table | Convenient filtered view for exploratory co-observation work |
| dryad_sighting_groups.csv | One row per nonblank exact Dryad sighting ID | Counts and distinct named J IDs, unresolved/missing row counts, and conflicts in grouped fields |
| data_dictionary.csv | All output columns and their origin | Distinguishes original source fields from added fields |

`validation_summary.json` records counts, original-input SHA-256 hashes and successful original-cell preservation checks. `preprocess.py` rebuilds the tables with pandas/openpyxl. Run `python preprocess.py` from any working directory after installing those dependencies in your own environment.

## Changes from the earlier version 3

- The main observation table now retains missing IDs and unresolved `u...` labels. The J-only table is an additional view rather than the only observation output.
- Raw source columns are preserved without replacing their values, including Museum `SightDate`, Dryad `DateTimeRounded`, `DateTimeJitter`, `sid_rounded`, method/model flags and all lifespan values.
- Exact repeated rows are flagged and retained. They may reflect reporting or sampling behavior and are not automatically removed.
- Every full-table row has a source filename and source row. Dryad observations link to lifespan rows only by an exact trimmed ID match.
- Literal `NA` ID cells are retained in the original `ID` column and treated as missing in the derived `whale_id`. Missing time tokens likewise do not become invented times.

## Interpretation rules

1. These CSVs are data preparation tables, not a revised conceptual ERD or a final relational schema. Generated row keys support traceability.
2. Keep Museum group reports separate from individual observations. Never expand a pod report into confirmed sightings of all its members. `j_label_mention` is a text-search flag, not proof of J-pod presence.
3. Named J IDs are candidates, not individually confirmed sightings. These files do not give a per-row confirmed/inferred label or identification basis. `identification_status` explicitly remains undetermined; `robust`, `drone`, `acoustic` and `theodolite` retain their source meanings and are not converted into individual-confirmation labels. `u...` labels remain unresolved and are not assumed to be stable whale identities.
4. Distinct named J IDs sharing an exact original `sighting_id` can support exploratory recorded co-observation queries. Count each whale once per sighting when generating pairs; repeated rows must not multiply edge counts. Shared observations do not prove close social ties. No association scores or predicted ties are invented here.
5. Dryad dates and coordinates remain shifted/obfuscated. Its x/y values remain in projected kilometres, not latitude/longitude degrees. `datetime_utc_shifted` parses the source UTC notation but does not recover actual times. Do not match Museum and Dryad encounters using dates or coordinates, or assume different source IDs refer to different biological encounters across providers. No cross-source encounter joins are made.
6. Museum times are parsed only where a valid HH:MM[:SS] is supplied. Missing times stay missing, and the time zone remains unspecified. Primary and alternate coordinates are both retained; range checks do not establish accuracy. UTM zone/datum are not supplied in these inputs and are not invented.
7. A `2050-01-01` lifespan sentinel is preserved in the original field and omitted from parsed biological-date fields. A death sentinel means no actual death date is supplied; do not infer that the whale is alive today. January 1 birth dates are retained without assuming day-level precision. Birth/death comparisons use shifted observation dates, so out-of-range flags require review and are not automatic exclusions.
8. Names, sex, mother-offspring links, verified matrilines, verified kinship and independently validated social relationships cannot be populated from these three files. Add a documented identity/family source before filling those parts of OrcaLink. No missing biological values have been invented.

## Source references

- Museum source: `Htut_UniversityOfVictoria_9.2026.csv`, supplied directly to the OrcaLink project. Original reporting-source labels remain in `Source`.
- Dryad source: `Copy of data_in.xlsx` and `Copy of lifespans_J.xlsx`, associated with https://doi.org/10.5061/dryad.gf1vhhn2f . Dataset-level shifted-coordinate/time and potential group-inference caveats follow the project source notes; they are not recoverable per-row identification judgments.

This package is for the project team's working use. The inclusion of source files does not change the provider's data-release conditions.
