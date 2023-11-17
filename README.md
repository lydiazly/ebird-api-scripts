# ebird-api-scripts

_**(In progress)**_

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Overview](#overview)
- [Requirements](#requirements)
- [Usage](#usage)
  - [User constants](#user-constants)
  - [Download historical observation data](#download-historical-observation-data)
  - [Download species table from eBird](#download-species-table-from-ebird)
  - [Download alpha species codes from](#download-alpha-species-codes-from)
- [Directory structure](#directory-structure)
- [License](#license)

<!-- /code_chunk_output -->


## Overview

Download historical observation data from [eBird](https://ebird.org/).

The 4-letter species codes from [British Columbia Breeding Bird Atlas](https://www.birdatlas.bc.ca) and `speciesCode` from [eBird](https://ebird.org/) data are combined. If the codes or names from both sites are not matching, there will be a 'Needs review' comment in each of these entries.


## Requirements

- Python 3.8
  - pandas, requests, beautifulsoup4


## Usage

### User constants

```
./constants.py
```

```python
#-- eBird API key -------------------------------------------------------------|
# (Can be reset by cli arguments)
API_KEY = ''
# The file contains the key
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from terminal

#-- Country, subnational1, subnational2, or location code ---------------------|
# (Can be reset by cli arguments)
# For observation data:
REGION_CODE_OBS = '...'
# For species list:
REGION_CODE_SPC = 'CA-BC'
...
```

### Download historical observation data

```
python ./get_obs.py [-h] [-f FORMAT [FORMAT ...]] [--region REGION] [--api API] [-t TABLE] [-s] [-d] [start_date] [end_date]
```

**Arguments**

- `start_date`            format: YYYY-MM-DD (default: 2023-11-01)
- `end_date`              format: YYYY-MM-DD (default: 2023-11-16)

optional arguments:
- `-h, --help`            show this help message and exit
- `-f FORMAT [FORMAT ...]` export format of observation data: {json, csv} (default: ('csv',))
- `--region REGION`       location code (default: L164543)
- `--api API`             API key, read from file '../eBird_API_Key.txt' if not specified
- `-t TABLE, --table TABLE` use the species table in this file (default: species/species_merged_CA-BC.csv)
- `-s, --species`         download species table then exit (default: False)
- `-d, --daily`           store daily data in JSON or CSV format (default: False)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName', 'count', 'exoticCategory']
```

### Download species table from eBird

```
python ./get_species.py [-h] [--region REGION] [--api API]
```

- `-h, --help`       show this help message and exit
- `--region REGION`  location code (default: CA-BC)
- `--api API`        API key, read from file '../eBird_API_Key.txt' if not specified

Output columns:

```
['speciesCode', 'comNameCode', 'bandingCode', 'sciNameCode', 'comName', 'sciName']
```

Can be called by `get_obs.py`.

### Download alpha species codes from

```
python ./get_bc_codes.py [-h] [--region REGION]
```

- `-h, --help`       show this help message and exit
- `--region REGION`  location code (default: CA-BC)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName']
```

Can be called by `get_obs.py`.

## Directory structure

```
├── {csv,json}/
│   ├── {YYYY}/
│   │   ├── obs_count_{YYYY-MM-DD}--{YYYY-MM-DD}.csv
│   │   └── ...
|   └── ...
└── species/
    ├── species_codes_bc.csv
    ├── species_ebird_{REGION}.csv
    ├── species_merged_{REGION}.csv
    └── ...
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.