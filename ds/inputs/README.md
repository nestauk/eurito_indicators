# Inputs

## Datasets

### CORDIS

#### `cordis_parse_opts.json`

kwargs for parsing data in CORDIS datasets

#### `cordis_read_opts.json`

kwargs for reading CORDIS datasets with `pd.read_csv`

#### `{fp}_organizations.csv`

- fp is in {fp1, fp2, fp3, fp4, fp5, fp6, fp7, h2020}

#### `{fp}_projects.csv`

- fp is in {fp1, fp2, fp3, fp4, fp5, fp6, fp7, h2020}

#### `{fp}_reports.csv`

- fp is in {fp7, h2020}

#### `h2020_project_deliverables.csv`

#### `h2020_project_publications.csv`

### SDG

#### `annotated/sdg_{goal}.csv`

Crowd annotated CORDS projects. Each file relates to one of the SDGs.

- goal is in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}

#### `official/sdg_hex_color_codes.json`

Lookup mapping SDG numbers to their official hex color codes.

#### `official/sdg_names.json`

Lookup mapping SDG numbers to their full official names.

