#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieves species list in a region from ebird.org and returns a csv.
[Python] 3.8
[Pkgs] pandas
"""
# 2023-11-11 created by Lydia
# 2023-11-16 last modified by Lydia
###############################################################################|
import requests
import pandas as pd
import sys
from io import StringIO

from modules.export_func import export
from constants import *

###############################################################################|
def get_species(session: requests.Session, url_dict: dict, region_code: str, headers: dict) -> pd.DataFrame:
    species_df = pd.DataFrame()
    
    #-- Download species codes in a region ------------------------------------|
    query_type = 'species'
    url_full = url_dict[query_type].format(region_code=region_code)
    print(f"Downloading species from '{url_full}' ...")
    response = session.get(url_full, headers=headers)
    if response.status_code == 200:
        species_list = response.json()
    else:
        sys.exit(f"GET request failed.\nStatus code: {response.status_code}")
    
    #-- Download subspecies ---------------------------------------------------|
    query_type = 'subspecies'
    print(f"Downloading subspecies from '{url_dict[query_type]}' ...")
    subspecies_list = []
    for species_code in species_list:
        if species_code in INCLUDE_SUBSPECIES.keys():
            # Get subspecies
            url_full = url_dict[query_type].format(speciesCode=species_code)
            response = session.get(url_full, headers=headers)
            if response.status_code == 200:
                sub_list = response.json()
                # If subspecies are found, append new entries
                if sub_list:
                    if INCLUDE_SUBSPECIES[species_code]:
                        for s in sub_list:
                            if s in INCLUDE_SUBSPECIES[species_code]:
                                subspecies_list.append(s)
                                print(f"> Appended subspecies of {species_code}: {s}")
                    else:
                        subspecies_list.extend(sub_list)
                        print(f"> Appended subspecies of {species_code}: {sub_list}")
            else:
                sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    species_list.extend(subspecies_list)
    
    #-- Download names --------------------------------------------------------|
    query_type = 'taxa'
    print(f"Downloading names from '{url_dict[query_type]}' ...")
    df_names = []
    for species_code in species_list:
        # Get names
        url_full = url_dict[query_type].format(speciesCode=species_code)
        response = session.get(url_full, headers=headers)
        if response.status_code == 200:
            data = response.text
            cols = list(TAXA_COLUMN_DICT.keys())
            df = pd.read_csv(StringIO(data), usecols=cols)[cols].rename(columns=TAXA_COLUMN_DICT)
            print(f"{species_code} -- {df['comName'].item()}")
            df_names.append(df)
        else:
            sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    
    species_df = pd.concat(df_names, axis=0)
    print(f"{species_df.columns.to_list()}\n")
    
    return species_df

###############################################################################|
if __name__ == '__main__':
    #--------------------------------------------------------------------------|
    # Parse arguments
    #--------------------------------------------------------------------------|
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default=REGION_CODE_SPC, help='location code (default: %(default)s)')
    parser.add_argument('--api', default=API_KEY, help=f"API key, read from file '{API_FILE}' if not specified")
    args = parser.parse_args()
    
    region_code = args.region
    api_key = args.api
    
    try:
        print(f"Reading API key from '{API_FILE}'")
        with open(API_FILE, 'r', newline="") as f:
            api_key = f.readline().strip()
    except:
        print(f"Not found.")
        api_key = input(f"Please enter the eBird API key: ")
    if not api_key:
        sys.exit(f"Exit.")
    headers = {'X-eBirdApiToken': api_key}
    
    session = requests.Session()
    species_df = get_species(session, URL_DICT, region_code, headers)
    
    if not species_df.empty:
        export(species_df, 'csv',
               EXPORT_FILE['species_ebird'].format(region_code=region_code),
               subdir='species')
        print(f"    ({species_df.shape[0]} species)")