#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieves observation data from ebird.org and returns a table with monthly counts.
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
import os
from io import StringIO

# -- eBird API key --
api_key = 'ji1p6han22uh'

# -- Region code --
location_code = 'L164543' # North Vancouver--Maplewood Conservation Area

# -- Target URL --
base_url = "https://api.ebird.org/v2"
url = {
    'species': base_url + "/product/spplist/{regionCode}",
    'taxonomy': base_url + "/ref/taxonomy/ebird?species={speciesCode}",
    'historical': base_url + "/data/obs/{regionCode}/historic/{y}/{m}/{d}",
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
    'species': "species_dict_{location_code}",
    'historical': "obs_historical_{start_date}", # JSON only
    'merged': "obs_count_{start_date}--{end_date}",
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
            print(e)
            raise
    
    if suffix == 'json':
        if isinstance(data, str):
            with open(fullpath, 'w') as f:
                f.write(data)
        else:
            data.to_json(fullpath, orient='records', indent=4)
            
    elif suffix == 'csv':
        data.to_csv(fullpath, sep=',', index=False, header=True,
                    quoting=csv.QUOTE_NONNUMERIC,
                    lineterminator='\n',
                    encoding='utf-8')
    print(f"--> Exported to: {fullpath}")

###############################################################################|
def main():
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d') if START_DATE else datetime.now().replace(day=1)
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d') if END_DATE else datetime.now() - timedelta(days=1)
    
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('dates', metavar='date', nargs='*',
                        help=f"format: YYYY-MM-DD (default: [{start_date.strftime('%Y-%m-%d')}, {end_date.strftime('%Y-%m-%d')}])")
    parser.add_argument('-s', '--species', action='store_true', help='(re)download species list (default: %(default)s)')
    parser.add_argument('-d', '--daily', action='store_true', help='(re)download species list (default: %(default)s)')
    args = parser.parse_args()
    
    download_species = args.species
    num_dates = len(args.dates)
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d') if END_DATE else datetime.now() - timedelta(days=1)
    if num_dates > 0:
        start_date = datetime.strptime(args.dates[0], '%Y-%m-%d')
    if num_dates > 1:
        end_date = datetime.strptime(args.dates[1], '%Y-%m-%d')
    
    headers = {'X-eBirdApiToken': api_key}
    
    print(f"[Start date] {start_date.strftime('%b %d, %Y')}")
    print(f"[End date]   {end_date.strftime('%b %d, %Y')}")
    print("Connecting...\n")
    
    #--------------------------------------------------------------------------|
    # Get species & names
    try:
        # If exist, read
        input_file = f"csv/{export_file['species'].format(location_code=location_code)}.csv"
        print(f"Reading data from '{input_file}'...\n")
        species_df = pd.read_csv(input_file, sep=',', header=0,
                        engine='python',
                        skipinitialspace=True,
                        quoting=csv.QUOTE_NONNUMERIC,
                        encoding='utf-8')
        print(f"Read data from '{input_file}' exists, skip downloading.")
    except FileNotFoundError:
        download_species = True

    if download_species:
        #----------------------------------------------------------------------|
        # Download species
        query_type = 'species'
        response = requests.get(url[query_type].format(regionCode=location_code),
                                headers=headers)
        if response.status_code == 200:
            data = response.json()
            json_object = json.dumps(data, indent=4)
            species_df = pd.DataFrame(data, columns=[primary_key])
            export(json_object, 'json', export_file[query_type].format(location_code=location_code))
        #----------------------------------------------------------------------|
        # Download names
        query_type = 'taxonomy'
        print("Downloading species...")
        df_names = []
        for species_code in species_df[primary_key]:
            print(f"  {species_code}")
            response = requests.get(url[query_type].format(speciesCode=species_code),
                                    headers=headers)
            if response.status_code == 200:
                data = response.text
                cols = list(column_names_dict.keys())
                df = pd.read_csv(StringIO(data), usecols=cols)[cols].rename(columns=column_names_dict)
                df_names.append(df)
        
        species_df = pd.concat(df_names, axis=0)
        export(species_df, 'csv', export_file['species'].format(location_code=location_code))
    
    print(f"({species_df.shape[0]} species)\n")
    # exit(0)
    
    #--------------------------------------------------------------------------|
    # Download obervation data
    query_type = 'historical'
    current_date = end_date
    print("Downloading obervation data...")
    while current_date >= start_date:
        merged_df = species_df.copy()
        merged_df[column_of_count] = 0
        last_date = current_date
        print(f">> {last_date.strftime('%B, %Y')} <<")
        # For each month
        while current_date.month == last_date.month:
            response = requests.get(url[query_type].format(regionCode=location_code,
                                                           y=current_date.year,
                                                           m=current_date.month,
                                                           d=current_date.day),
                                    headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    json_object = json.dumps(data, indent=4)
                    df = pd.DataFrame(data)
                    # -- Export JSON ------------------------------------------|
                    # export(json_object, 'json',
                    #     export_file[query_type].format(start_date=current_date.strftime('%Y-%m-%d')),
                    #     subdir=os.path.join(location_code, str(current_date.year), str(current_date.month)))
                    # print(f"    ({df.shape[0]} rows x {df.shape[1]} columns)")
                    #----------------------------------------------------------|
                    merged_df = pd.merge(merged_df, df[selected_columns], on=selected_columns, how='outer')
                
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
        for suffix in ['csv', 'json']:
            export(merged_df, suffix,
                export_file['merged'].format(start_date=date0_str, end_date=date1_str),
                subdir=os.path.join(location_code, str(last_date.year)))
        print(f"    ({merged_df.shape[0]} rows x {merged_df.shape[1]} columns)")

###############################################################################|
if __name__ == '__main__':
    main()
