#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieves observation data in a region from ebird.org and returns a table with monthly counts.
- eBird API key is needed
- 'X' and any other non-numeric values are ignored and will be counted as 0
- If `species_dict.csv` exists, read from it unless `--species` is specified

[In] cli arguments (see `-h`)
[Out] json, csv
Directory structure:
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

[Python] 3.8
[Pkgs] requests, pandas
[References]
  eBird API 2.0: https://documenter.getpostman.com/view/664302/S1ENwy59
  API key request: https://ebird.org/api/keygen

TODO:
[x] Read API key from file or terminal
[x] Session
[x] Subspecies
[x] Merge BC code
[x] Organize the code
[ ] Google sheets
[ ] Add comment column
"""
# 2023-11-09 created by Lydia
# 2023-11-16 last modified by Lydia
###############################################################################|
import argparse
from datetime import datetime, timedelta
import requests
import pandas as pd
import csv
import os
import sys

from modules.export_func import export
from get_species import get_species
from get_bc_codes import get_bc_codes
from constants import *

#-- Default dates --
# Will be reset by cli arguments
START_DATE_STR = '' # If empty, set to the first day of the current month
END_DATE_STR = '' # If empty, set to yesterday

#-- Input/Output date format --
DATE_FORMAT = '%Y-%m-%d' # ISO 8601 format: YYYY-MM-DD

###############################################################################|
def main():
    start_date = datetime.strptime(START_DATE_STR, DATE_FORMAT) if START_DATE_STR else datetime.now().replace(day=1)
    end_date = datetime.strptime(END_DATE_STR, DATE_FORMAT) if END_DATE_STR else datetime.now() - timedelta(days=1)
    
    #--------------------------------------------------------------------------|
    # Parse arguments
    #--------------------------------------------------------------------------|
    parser = argparse.ArgumentParser()
    parser.add_argument('start_date', nargs='?', default=start_date.strftime(DATE_FORMAT), help="format: YYYY-MM-DD (default: %(default)s)")
    parser.add_argument('end_date', nargs='?', default=end_date.strftime(DATE_FORMAT), help="format: YYYY-MM-DD (default: %(default)s)")
    parser.add_argument('-f', dest='formats', metavar='FORMAT', nargs='+', default=('csv',), choices={'csv', 'json'},
                        help='export format of observation data: {%(choices)s} (default: %(default)s)')
    parser.add_argument('--region', default=REGION_CODE_OBS, help='location code (default: %(default)s)')
    parser.add_argument('--api', default=API_KEY, help=f"API key, read from file '{API_FILE}' if not specified")
    parser.add_argument('-t', '--table', default=SPECIES_TABLE, help="use the species table in this file (default: %(default)s)")
    parser.add_argument('-s', '--species', action='store_true', help="download species table then exit (default: %(default)s)")
    parser.add_argument('-d', '--daily', action='store_true', help='store daily data in JSON or CSV format (default: %(default)s)')
    args = parser.parse_args()
    
    export_formats = set(args.formats)
    download_species = args.species
    download_daily = args.daily
    region_code = args.region
    api_key = args.api
    species_file = args.table

    if args.start_date:
        start_date = datetime.strptime(args.start_date, DATE_FORMAT)
    if args.end_date:
        end_date = datetime.strptime(args.end_date, DATE_FORMAT)
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if not api_key:
        try:
            print(f"Reading API key from '{API_FILE}'")
            with open(API_FILE, 'r', newline="") as f:
                api_key = f.readline().strip()
        except:
            print(f"Not found.")
            api_key = input(f"Please enter the eBird API key: ")
        if not api_key:
            sys.exit("Exit.")
    headers = {'X-eBirdApiToken': api_key}

    print(f"[API key]     {api_key}")
    print(f"[Region code] {region_code}")
    print(f"[Start date]  {start_date.strftime('%b %d, %Y')}")
    print(f"[End date]    {end_date.strftime('%b %d, %Y')}\n")
    
    #--------------------------------------------------------------------------|
    # Get species & names
    #--------------------------------------------------------------------------|
    species_df = pd.DataFrame()
    if not download_species:
        try:
            # Read species codes (Bird Atlas BC codes included)
            species_df = pd.read_csv(species_file, sep=',', header=0,
                                     skipinitialspace=True,
                                     quoting=csv.QUOTE_NONNUMERIC,
                                     encoding='utf-8')
            print(f"Imported data from '{species_file}'.")
            print(f"  {species_df.columns.to_list()}")
            print(f"({species_df.shape[0]} species)\n")
        except FileNotFoundError:
            print(f"File '{species_file}' is not found.")
            go_download = input(f"Download? (y/[n]) ")
            if go_download != "y":
                sys.exit("Exit.")
    
    session = requests.Session()
    
    #-- Download species codes and names in a region --------------------------|
    if species_df.empty:
        species_df = get_species(session, URL_DICT, REGION_CODE_SPC, headers)
        export(species_df, 'csv',
               EXPORT_FILE['species_ebird'].format(region_code=REGION_CODE_SPC),
               subdir='species')
        print(f"    ({species_df.shape[0]} species)\n")
        
        #-- Get the alpha codes from www.birdatlas.bc.ca ----------------------|
        species_df = get_bc_codes(session, REGION_CODE_SPC)
        if not species_df.empty:
            # Export to CSV
            export(species_df, 'csv',
                   EXPORT_FILE['species_merged'].format(region_code=REGION_CODE_SPC),
                   subdir='species')
            print(f"    ({species_df.shape[0]} species)")
        
        if download_species:
            sys.exit(0)
    
    #--------------------------------------------------------------------------|
    # Download obervation data
    #--------------------------------------------------------------------------|
    query_type = 'obs'
    current_date = end_date
    print("Downloading obervation data...")
    while current_date >= start_date:
        merged_df = species_df
        merged_df[COUNT_COL] = 0
        last_date = current_date
        print(f"\n== {last_date.strftime('%B, %Y')} ==")
        # For each month
        while current_date.month == last_date.month:
            day, month, year = current_date.day, current_date.month, current_date.year
            
            url_full = URL_DICT[query_type].format(region_code=region_code,
                                              y=year, m=month, d=day)
            response = session.get(url_full, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    #-- Export daily data -------------------------------------|
                    if download_daily:
                        for fmt in export_formats:
                            export(data if fmt == 'json' else df, fmt,
                                   EXPORT_FILE[query_type].format(start_date=current_date.strftime(DATE_FORMAT)),
                                   subdir=os.path.join(fmt, region_code, str(year), str(month)))
                        print(f"    ({df.shape[0]} rows x {df.shape[1]} columns)")
                    #-- Merge columns -----------------------------------------|
                    # 'howMany' -> 'howMany','howMany_day1', 'howMany_day2', ...
                    cols = [CODE_EBIRD, COUNT_COL]
                    for col in df.columns:
                        if col in EXTRA_COLS:
                            cols.append(col)
                    merged_df = pd.merge(merged_df, df[cols],
                                         on=CODE_EBIRD, how='left',
                                         suffixes=['', f'_{day}'])
                    #-- Append missing rows -----------------------------------|
                    missing_mask = ~df[CODE_EBIRD].isin(merged_df[CODE_EBIRD])
                    if missing_mask.any():
                        new_rows = df.loc[missing_mask, OBS_COLS]
                        merged_df = pd.concat([merged_df, new_rows], ignore_index=True)
                        print("Appended: ", new_rows['speciesCode'].to_list())
            else:
                sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
            
            current_date -= timedelta(days=1)
            
        #-- Replace non-numeric values with 0, then fill NaN with 0 -----------|
        count_columns = [col for col in merged_df.columns if 'howMany' in col]
        merged_df[count_columns] = merged_df[count_columns] \
                                    .apply(pd.to_numeric, errors='coerce') \
                                    .fillna(0).astype('int64')
        #-- Sum the 'howMany_*' columns ---------------------------------------|
        merged_df[EXPORT_COUNT_COL] = merged_df[count_columns].sum(axis=1)
        
        #-- Extra columns -----------------------------------------------------|
        # Append all the non-null different values into one column
        for extra_col in EXTRA_COLS:
            extra_columns = [col for col in merged_df.columns if extra_col in col]
            merged_df[extra_col] = merged_df[extra_columns].apply(lambda x: ' '.join(set(x.dropna())), axis=1)
        
        merged_df = merged_df[EXPORT_OBS_COLS].rename(columns=OBS_COLUMN_DICT)
        
        #-- Export monthly data -----------------------------------------------|
        date0_str = last_date.replace(day=1).strftime(DATE_FORMAT) # First day of the month
        date1_str = last_date.strftime(DATE_FORMAT)
        print("\nMerged:")
        print(f"  {merged_df.columns.to_list()}\n")
        for fmt in export_formats:
            export(merged_df, fmt,
                   EXPORT_FILE['obs_merged'].format(start_date=date0_str, end_date=date1_str),
                   subdir=os.path.join(fmt, region_code, str(last_date.year)))
        print(f"    ({merged_df.shape[0]} rows x {merged_df.shape[1]} columns)")

###############################################################################|
if __name__ == '__main__':
    main()
