# ebird-api-scripts

_(In progress)_

Download historical observation data in a particular region from [eBird](https://ebird.org/).

The 4-letter species codes from [BC Breeding Bird Atlas](https://www.birdatlas.bc.ca) (referred to as "BC code") and `speciesCode` from [eBird](https://ebird.org/) data are combined automatically. If any eBird entry does not match any Bird Atlas species entry, the script `get_obs.py` will append a comment and attempt to match it with other attributes, then follow these rules:
- If the match does not contain eBird data, fill in.
- If the match already contains eBird data, append the eBird data right below it.

For detailed information and available options of each script, see `-h` or `--help`.

**TODO**
- [x] Combine the species codes and make a lookup table
- [ ] Append other required attributes.
- [ ] Check subspecies to be retrieved
- [ ] Combine manually defined information into the species table to eliminate the mismatches
- [ ] Import/Export Google Sheets
- [ ] Merge into other data
- [ ] Update documentation

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=6 orderedList=false} -->

**Table of Contents**

<!-- code_chunk_output -->

- [Requirements](#requirements)
- [Usage](#usage)
  - [Edit user constants](#edit-user-constants)
  - [Download historical observation data](#download-historical-observation-data)
  - [Download species table from eBird](#download-species-table-from-ebird)
  - [Download species codes from BC Breeding Bird Atlas](#download-species-codes-from-bc-breeding-bird-atlas)
- [Directory structure](#directory-structure)
- [License](#license)

<!-- /code_chunk_output -->


## Requirements

- Python 3.8
  - pandas, requests, beautifulsoup4


## Usage

### Edit user constants

```
./constants.py
```

```python
#-- eBird API key --
# (Can be reset by cli arguments)
API_KEY = ''
# The file contains the key
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from the terminal

#-- Country, subnational1, subnational2, or location code --
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

This script calls `get_species.py` and `get_bc_codes.py` to download the species table.

**Arguments**

- `start_date`            Format: YYYY-MM-DD (default: the first day of this month)
- `end_date`              Format: YYYY-MM-DD (default: yesterday)

optional arguments:
- `-f FORMAT [FORMAT ...]` Export format of observation data: {json, csv} (default: ('csv',))
- `--region REGION`       Location code (default: L164543)
- `--api API`             API key, read from file if not specified
- `-t TABLE, --table TABLE` Use the species table in this file (default: species/species_merged_CA-BC.csv)
- `-s, --species`         Download the species table then exit (default: False)
- `-d, --daily`           Store daily data in JSON or CSV format (default: False)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName', 'count', 'exoticCategory']
```

### Download species table from eBird

```
python ./get_species.py [-h] [--region REGION] [--api API]
```

Can be standalone or called by `get_obs.py`.

- `-h, --help`       Show this help message and exit
- `--region REGION`  Location code (default: CA-BC)
- `--api API`        API key, read from file '../eBird_API_Key.txt' if not specified

Output columns:

```
['speciesCode', 'comNameCode', 'bandingCode', 'sciNameCode', 'comName', 'sciName']
```

See the [sample](https://drive.google.com/file/d/1-bbMrjWZNcQr7BxJiD6rPGlo38eNlMyc/view?usp=share_link).

### Download species codes from BC Breeding Bird Atlas

```
python ./get_bc_codes.py [-h] [--region REGION]
```

Can be standalone or called by `get_obs.py`.

- `-h, --help`       Show this help message and exit
- `--region REGION`  Location code (default: CA-BC)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName']
```

See this [sample](species_ebird_L164543.csv) and [output log](species_merged_CA-BC.log).

## Directory structure

```
├── {csv,json}/
│   ├── {YEAR}/
│   │   ├── obs_count_{YYYY-MM-DD}--{YYYY-MM-DD}.csv
│   │   └── ...
|   └── ...
└── species/
    ├── species_codes_bc.csv
    ├── species_ebird_{REGION}.csv
    └── species_merged_{REGION}.csv
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.