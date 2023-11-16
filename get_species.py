#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieves species list in a region from ebird.org and returns a csv.
[Python] 3.8
[Pkgs] pandas
"""
# 2023-11-11 created by Lydia
# 2023-11-15 last modified by Lydia
###############################################################################|
import requests
import pandas as pd
import sys
from io import StringIO

from modules.export_func import export
from constants import *

REGION_CODE = 'CA-BC'
# REGION_CODE = 'L164543'

# -- Map the columns from taxonomy data to the merged table --
COLUMN_NAME_DICT = {
    'SPECIES_CODE'   : 'speciesCode',
    'COM_NAME_CODES' : 'comNameCode',
    'BANDING_CODES'  : 'bandingCode',
    'SCI_NAME_CODES' : 'sciNameCode',
    'COMMON_NAME'    : 'comName',
    'SCIENTIFIC_NAME': 'sciName',
}

INCLUDE_SUBSPECIES = ['yerwar', 'rethaw']

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
        if species_code in INCLUDE_SUBSPECIES:
            # Get subspecies
            url_full = url_dict[query_type].format(speciesCode=species_code)
            response = session.get(url_full, headers=headers)
            if response.status_code == 200:
                sub_list = response.json()
                # If subspecies are found, append new entries
                if len(sub_list) > 1:
                    subspecies_list.extend(sub_list)
                    print(f"> Appended subspecies of {species_code}: {sub_list}")
            else:
                sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    species_list.extend(subspecies_list)
    
    #-- Download names --------------------------------------------------------|
    query_type = 'taxonomy'
    print(f"Downloading names from '{url_dict[query_type]}' ...")
    df_names = []
    for species_code in species_list:
        # Get names
        url_full = url_dict[query_type].format(speciesCode=species_code)
        response = session.get(url_full, headers=headers)
        if response.status_code == 200:
            data = response.text
            cols = list(COLUMN_NAME_DICT.keys())
            df = pd.read_csv(StringIO(data), usecols=cols)[cols].rename(columns=COLUMN_NAME_DICT)
            print(f"{species_code} -- {df['comName'].item()}")
            df_names.append(df)
        else:
            sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    
    species_df = pd.concat(df_names, axis=0)
    
    return species_df

###############################################################################|
if __name__ == '__main__':
    api_key = ''
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
    species_df = get_species(session, URL_DICT, REGION_CODE, headers)
    
    if not species_df.empty:
        export(species_df, 'csv', f"species_ebird_{REGION_CODE}", subdir='species')
        print(f"    ({species_df.shape[0]} species)")