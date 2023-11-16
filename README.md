# ebird-api-scripts

### Scripts

[Tested Python version] Python 3.8

- Download historical observation data
```
python ./get_obs.py [-h] [-f FORMAT [FORMAT ...]] [--region REGION] [--api API] [-s] [-d] [start_date] [end_date]
```

>   start_date:            format: YYYY-MM-DD (default: 2023-11-01)
>   end_date:              format: YYYY-MM-DD (default: 2023-11-14)
>   -h, --help:            show this help message and exit
>   -f FORMAT [FORMAT ...]: export format of observation data: {json, csv} (default: ('csv',))
>   --region REGION:       location code (default: L164543)
>   --api API:             API key, read from file '../eBird_API_Key.txt' if not specified
>   -s, --species:         download species list then exit (default: False)
>   -d, --daily:           store daily data in JSON or CSV format (default: False)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName', 'count', 'exoticCategory']
```

- Download species list from eBird

```
python ./get_species.py [-h] [--region REGION] [--api API]
```

>  -h, --help:       show this help message and exit
>  --region REGION:  location code (default: CA-BC)
>  --api API:        API key, read from file '../eBird_API_Key.txt' if not specified

Output columns:

```
['speciesCode', 'comNameCode', 'bandingCode', 'sciNameCode', 'comName', 'sciName']
```
- Download alpha species codes from

```
python ./get_bc_codes.py [-h] [--region REGION]
```

>  -h, --help:       show this help message and exit
>  --region REGION:  location code (default: CA-BC)

Output columns:

```
['alphaCode_bc', 'bandingCode', 'comNameCode', 'speciesCode', 'comName', 'comName_ebird', 'sciName']
```

### Directory structure

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