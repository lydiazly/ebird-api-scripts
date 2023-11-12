#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieves observation data in a region from ebird.org and returns a table with monthly counts.
- 'X' is ignored and will be counted as 0.
- An eBird API key is needed.
- If `species_dict.csv` exists, read from it unless `--species` is specified

[In] strings of dates in iso format
[Out] json, csv
Directory structure:
├── csv
│   ├── {year}
│   │   ├── obs_count_YYYY-MM-DD--YYYY-MM-DD.csv
│   │   └── ...
└── json
    ├── {year}
    │   ├── obs_count_YYYY-MM-DD--YYYY-MM-DD.json
    │   └── ...
    └── species_dict.json

[Python] 3.8
[Pkgs] pandas
[References]
  eBird API 2.0: https://documenter.getpostman.com/view/664302/S1ENwy59
  API key request: https://ebird.org/api/keygen

TODO:
[x] Read API key from file or terminal
[x] Session
[ ] async
[ ] Merge monthly data of one year into one file
[ ] Add hotspot info
[ ] Map the BC code
[ ] Merge BC code
"""
# 2023-11-09 created by Lydia
# 2023-11-10 last modified by Lydia
###############################################################################|
import argparse
from datetime import datetime, timedelta
import requests
import pandas as pd
import csv
import json
import sys
import os
from io import StringIO

# -- eBird API key --
API_KEY = ''
api_file = "../eBird_API_Key.txt" # If the file does not exist, read from terminal

# -- Country, subnational1, subnational2, or location code --
REGION_CODE = 'L164543' # North Vancouver--Maplewood Conservation Area

# -- Target URL --
base_url = "https://api.ebird.org/v2"
url = {
    'hotspot': base_url + "/ref/hotspot/info/{region_code}",
    'species': base_url + "/product/spplist/{region_code}",
    'taxonomy': base_url + "/ref/taxonomy/ebird?species={speciesCode}",
    'historical': base_url + "/data/obs/{region_code}/historic/{y}/{m}/{d}",
}

# -- Default dates --
# Will be reset by cli arguments (ISO 8601 format: YYYY-MM-DD)
START_DATE = '' # '': 1st day of the current month
END_DATE = '' # '': yesterday

# -- Export date format --
export_date_format = '%Y-%m-%d' # YYYY-MM-DD

# -- Primary key --
primary_key = 'speciesCode' # should be the same in the historical and the merged

# -- Selected columns in the historical data on a given date --
selected_columns = ['speciesCode', 'comName', 'sciName', 'howMany']
column_of_count = 'howMany'

# -- Columns in the output --
export_columns = ['speciesCode', 'comName', 'sciName', 'count']
export_column_of_count = 'count'

# -- Map the columns from taxonomy data to the merged table --
column_names_dict = {'SPECIES_CODE': primary_key,
                     'COMMON_NAME': 'comName',
                     'SCIENTIFIC_NAME': 'sciName'}

# -- Export files --
# filename without suffix
export_file = {
    'species': "species_ebird_{region_code}",
    'historical': "obs_ebird_{start_date}",
    'merged': "obs_ebird_{start_date}--{end_date}",
}

###############################################################################|
def export(data, suffix, filename, subdir=''):
    """
    Export to CSV or JSON. Data can be str or DataFrame.
    """
    dirname = os.path.join(suffix, subdir)
    fullpath = f"{dirname}/{filename}.{suffix}"
    if not os.path.isdir(dirname):
        try:
            os.makedirs(dirname)
            print(f"Directory '{dirname}' created.")
        except OSError as e:
            sys.exit(e)
    
    if suffix == 'json':
        if isinstance(data, list):
            json_object = json.dumps(data, indent=4)
            with open(fullpath, 'w') as f:
                f.write(json_object)
        elif isinstance(data, pd.core.frame.DataFrame):
            data.to_json(fullpath, orient='records', indent=4)
        else:
            sys.exit(f"Unsupported data type {type(data)}.")
    elif suffix == 'csv':
        if isinstance(data, pd.core.frame.DataFrame):
            data.to_csv(fullpath, sep=',', index=False, header=True,
                        quoting=csv.QUOTE_NONNUMERIC,
                        lineterminator='\n',
                        encoding='utf-8')
        else:
            sys.exit(f"Unsupported data type {type(data)}.")
    print(f"--> Exported to: {fullpath}")

###############################################################################|
def main():
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d') if START_DATE else datetime.now().replace(day=1)
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d') if END_DATE else datetime.now() - timedelta(days=1)
    
    # Parse arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('dates', metavar='date', nargs='*',
    #                     help=f"format: YYYY-MM-DD (default: [{start_date.strftime('%Y-%m-%d')}, {end_date.strftime('%Y-%m-%d')}])")
    parser.add_argument('start_date', nargs='?', default=start_date.strftime('%Y-%m-%d'), help="format: YYYY-MM-DD (default: %(default)s)")
    parser.add_argument('end_date', nargs='?', default=end_date.strftime('%Y-%m-%d'), help="format: YYYY-MM-DD (default: %(default)s)")
    parser.add_argument('-f', dest='formats', metavar='FORMAT', nargs='+', default=('csv',), choices={'csv', 'json'},
                        help='export format of observation data: {%(choices)s} (default: %(default)s)')
    parser.add_argument('--region', nargs='?', default=REGION_CODE, help='location code (default: %(default)s)')
    parser.add_argument('--api', nargs='?', default=API_KEY, help=f"API key, read from file '{api_file}' if not specified")
    parser.add_argument('-s', '--species', action='store_true',
                        help=f"(re)download species list as csv (default: %(default)s, read from 'species/{export_file['species']}.csv')")
    parser.add_argument('-d', '--daily', action='store_true', help='store daily data in JSON or CSV format (default: %(default)s)')
    args = parser.parse_args()
    
    export_formats = set(args.formats)
    download_species = args.species
    download_daily = args.daily
    region_code = args.region
    api_key = args.api

    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if not api_key:
        try:
            with open(api_file, 'r', newline="") as f:
                api_key = f.readline().strip()
        except:
            api_key = input(f"Please enter the eBird API key: ")
        if not api_key:
            sys.exit(f"Exit.")
    headers = {'X-eBirdApiToken': api_key}

    print(f"[API key]    {api_key}")
    print(f"[Region]     {region_code}")
    print(f"[Start date] {start_date.strftime('%b %d, %Y')}")
    print(f"[End date]   {end_date.strftime('%b %d, %Y')}")
    
    #--------------------------------------------------------------------------|
    # Get species & names
    if not download_species:
        try:
            # If exist, read
            input_file = f"species/{export_file['species'].format(region_code=region_code)}.csv"
            species_df = pd.read_csv(input_file, sep=',', header=0,
                                     skipinitialspace=True,
                                     quoting=csv.QUOTE_NONNUMERIC,
                                     encoding='utf-8')
            print(f"\nRead data from '{input_file}'.")
        except FileNotFoundError:
            download_species = True

    session = requests.Session()
    
    if download_species:
        #----------------------------------------------------------------------|
        # Download species codes in a region
        query_type = 'species'
        url_full = url[query_type].format(region_code=region_code)
        response = session.get(url_full, headers=headers)
        if response.status_code == 200:
            data = response.json()
            species_df = pd.DataFrame(data, columns=[primary_key])
        else:
            sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
        #----------------------------------------------------------------------|
        # Download names
        query_type = 'taxonomy'
        print("\nDownloading species...")
        df_names = []
        for species_code in species_df[primary_key]:
            # print(f"  {species_code}")
            url_full = url[query_type].format(speciesCode=species_code)
            response = session.get(url_full, headers=headers)
            if response.status_code == 200:
                data = response.text
                cols = list(column_names_dict.keys())
                df = pd.read_csv(StringIO(data), usecols=cols)[cols].rename(columns=column_names_dict)
                df_names.append(df)
            else:
                sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
        
        species_df = pd.concat(df_names, axis=0)
        export(species_df, 'csv',
               export_file['species'].format(region_code=region_code),
               subdir='species')
    
    print(f"({species_df.shape[0]} species)\n")
    
    #--------------------------------------------------------------------------|
    # Download obervation data
    query_type = 'historical'
    current_date = end_date
    print("Downloading obervation data...")
    while current_date >= start_date:
        merged_df = species_df.copy()
        merged_df[column_of_count] = 0
        last_date = current_date
        print(f"== {last_date.strftime('%B, %Y')} ==")
        # For each month
        while current_date.month == last_date.month:
            url_full = url[query_type].format(region_code=region_code,
                                              y=current_date.year,
                                              m=current_date.month,
                                              d=current_date.day)
            response = session.get(url_full, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    # -- Daily data ---------------------------------------- --|
                    if download_daily:
                        for fmt in export_formats:
                            export(data if fmt == 'json' else df, fmt,
                                   export_file[query_type].format(start_date=current_date.strftime('%Y-%m-%d')),
                                   subdir=os.path.join(region_code, str(current_date.year), str(current_date.month)))
                            print(f"    ({df.shape[0]} rows x {df.shape[1]} columns)")
                    #----------------------------------------------------------|
                    merged_df = pd.merge(merged_df, df[selected_columns], on=selected_columns, how='outer')
            else:
                sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
            
            current_date -= timedelta(days=1)
            
        #----------------------------------------------------------------------|
        # Replace 'X' or other non-numeric values with 0, then fill NaN values with 0
        merged_df[column_of_count] = pd.to_numeric(merged_df[column_of_count], errors='coerce')
        # Fill NaN values with 0
        merged_df[column_of_count].fillna(0, inplace=True)
        # Aggregate the counts for each speciesCode
        merged_df[export_column_of_count] = merged_df.groupby('speciesCode')[column_of_count].transform('sum').astype(int)
        # Drop duplicate columns and reset index
        merged_df = merged_df[export_columns].drop_duplicates().reset_index(drop=True)
        
        #----------------------------------------------------------------------|
        # Export monthly data
        date0_str = last_date.replace(day=1).strftime('%Y-%m-%d')
        date1_str = last_date.strftime('%Y-%m-%d')
        print(f"Merged:")
        for fmt in export_formats:
            export(merged_df, fmt,
                   export_file['merged'].format(start_date=date0_str, end_date=date1_str),
                   subdir=os.path.join(region_code, str(last_date.year)))
        print(f"    ({merged_df.shape[0]} rows x {merged_df.shape[1]} columns)")

###############################################################################|
if __name__ == '__main__':
    main()
