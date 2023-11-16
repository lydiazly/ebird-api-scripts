#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get the species codes from www.birdatlas.bc.ca, merge with eBird codes, and returns a table.
[In]
[Out] csv
[Python] 3.8
[Pkgs] pandas, beautifulsoup4
  conda install beautifulsoup4
"""
# 2023-11-11 created by Lydia
# 2023-11-15 last modified by Lydia
###############################################################################|
import requests
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import csv
import re
import sys

from modules.export_func import export
from constants import *

# URL = "https://www.birdatlas.bc.ca/bcdata/codes.jsp?lang=en&pg=species&sortorder=codes"
URL = URL_DICT['bc']

# -- Column names of bc code and eBird code --
CODE_EBIRD = 'speciesCode'
CODE_BC = 'alphaCode_bc'

CODE_REF1 = 'bandingCode' # Reference 1
CODE_REF2 = 'comNameCode' # Reference 2

# -- Column names of species names --
NAME_BC = 'comName'
NAME_EBIRD = NAME_BC + '_ebird'

# -- Columns for import/export --
COLUMN_NAMES_BC = [CODE_BC, NAME_BC]
EXPORT_COLUMN_NAMES = [CODE_BC, CODE_REF1, CODE_REF2, CODE_EBIRD, NAME_BC, NAME_EBIRD]

RENAME_DICT = {
    'speciesCode': 'speciesCode_ebird',
    'bandingCode': 'bandingCode_ebird',
    'comNameCode': 'comNameCode_ebird',
}

REGION_CODE = 'CA-BC'
# REGION_CODE = 'L164543'

# -- eBird codes table --
TABLE_EBIRD = f"species/species_ebird_{REGION_CODE}.csv"

# -- Export files --
# In species/
# filename without suffix
EXPORT_TABLE_BC = "species_codes_bc"
EXPORT_TABLE_MERGED = f"species_merged_{REGION_CODE}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
}
###############################################################################|
def get_bc_codes(session: requests.Session) -> pd.DataFrame:
    merged_df = pd.DataFrame()
    
    print("Connecting...")

    # Send an HTTP GET request
    response = session.get(URL, headers=HEADERS)
    if response.status_code == 200:
        # soup = BeautifulSoup(response.content, 'html.parser')
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup.contents); exit(0)
        
        #----------------------------------------------------------------------|
        # Find all <tr> elements that contain a <b> tag
        container = soup.find_all('div', id="innercontainer")
        if container:
            rows = container[0].find_all(lambda tag: tag.name == 'tr' and tag.get('valign') != "TOP")
            if rows:
                codes = []
                names = []
                for row in rows:
                    if isinstance(row, NavigableString):
                        continue
                    cols = row.find_all('td')
                    if cols and len(cols) == 2:
                        col1 = cols[0].b
                        if col1:
                            code = col1.text.strip()
                            name = cols[1].text.strip()
                            print(f"{code} -- {name}")
                            # Extract the code from the <b> tag in the first <td>
                            codes.append(row.find('td').b.text.strip())
                            # Extract the common name from the second <td>
                            names.append(row.find_all('td')[1].text.strip())
                df = pd.DataFrame({COLUMN_NAMES_BC[0]: codes, COLUMN_NAMES_BC[1]: names})

                # Export to CSV
                export(df, 'csv', EXPORT_TABLE_BC, subdir='csv')
                print(f"    ({df.shape[0]} species)")
            
                #--------------------------------------------------------------|
                try:
                    # If ebird codes exists, read
                    ebird_df = pd.read_csv(TABLE_EBIRD, sep=',', header=0,
                                           skipinitialspace=True,
                                           quoting=csv.QUOTE_NONNUMERIC,
                                           encoding='utf-8')
                    print(f"\nRead data from '{TABLE_EBIRD}'.")
                    
                    # Split names by ' or ' or '/'
                    name_tmp = NAME_BC + '_tmp'
                    df[name_tmp] = df[NAME_BC] \
                                        .apply(lambda x: re.sub(r'^(\w+)( or |\/)(\w+) (\w+)', r'\1 \4\2\3 \4', x))
                    
                    # Copy the primary key for further sorting
                    bc_key_tmp = CODE_BC + '_tmp'
                    df[bc_key_tmp] = df[CODE_BC]
                    
                    # Merge data
                    merged_df = pd.merge(df, ebird_df, on=NAME_BC, how='outer')
                    merged_df.to_csv('tmp.csv', sep=',', index=False, header=True,
                                     quoting=csv.QUOTE_NONNUMERIC,
                                     lineterminator='\n',
                                     encoding='utf-8')
                    
                    # Copy names
                    merged_df[NAME_EBIRD] = merged_df[NAME_BC]
                    
                    # Find the rows without bc codes
                    cols_ebird = [col for col in ebird_df.columns if col != NAME_BC]
                    
                    missing_ids = merged_df.index[merged_df[bc_key_tmp].isna()].to_list()
                    for idx in missing_ids:
                        name_ebird = str(merged_df.loc[idx, NAME_BC]).strip()
                        # Maybe matches one of the names in '... or ...' or '.../...'
                        match_row = df[df[name_tmp].str.contains(name_ebird, regex=False)]
                        if not match_row.empty:
                            # Copy code for sorting
                            merged_df.loc[idx, bc_key_tmp] = match_row[CODE_BC].values[0] + '0'
                            for name_bc in match_row[NAME_BC].to_list():
                                print(f"Found possible related names: {name_bc} -- {name_ebird} (ebird)")
                            continue
                        # Maybe one of the other codes matches
                        code1 = merged_df.loc[idx, CODE_REF1]
                        code2 = merged_df.loc[idx, CODE_REF2]
                        code_list = []
                        code_list.extend([code1] if not pd.isna(code1) else [])
                        code_list.extend([code2] if not pd.isna(code2) else [])
                        for code in code_list:
                            match_idx = merged_df.index[merged_df[CODE_BC] == code].to_list()
                            if match_idx:
                                if merged_df.loc[match_idx[0], CODE_EBIRD] is None:
                                    # Add values to the match
                                    merged_df.loc[match_idx[0], NAME_EBIRD] = merged_df.loc[idx, NAME_BC]
                                    merged_df.loc[match_idx[0], cols_ebird] = merged_df.loc[idx, cols_ebird]
                                    print(f"Found possible related code: {code} -- {name_ebird} (ebird)")
                                else:
                                    # Copy code for sorting
                                    merged_df.loc[idx, bc_key_tmp] = str(merged_df.loc[match_idx[0], CODE_BC]) + '0'
                                    print(f"Found possible related names: {merged_df.loc[match_idx[0], NAME_BC]} -- {name_ebird} (ebird)")
                                break
                    
                    # Drop extra entries
                    merged_df = merged_df.dropna(subset=bc_key_tmp)
                    
                    # Sort
                    merged_df = merged_df.sort_values(bc_key_tmp)[EXPORT_COLUMN_NAMES]
                    
                    # Rename
                    merged_df = merged_df.rename(columns=RENAME_DICT)
                    ebird_key = RENAME_DICT[CODE_EBIRD]
                    
                    # Check missing
                    missing_bc = merged_df.loc[merged_df[CODE_BC].isna(), :]
                    mask = merged_df[ebird_key].isna()
                    merged_df.loc[mask, NAME_EBIRD] = None
                    missing_ebird = merged_df.loc[mask, :]
                    if not missing_bc.empty:
                        print("\nMissing bc codes:\n", missing_bc)
                    if not missing_ebird.empty:
                        print("\nMissing ebird codes:\n", missing_ebird)
                    
                except FileNotFoundError:
                    print(f"'{TABLE_EBIRD}' is not found. Skip merging.")
    
    else:
        sys.exit(f"GET request failed. Status code: {response.status_code}")
    
    return merged_df
    
###############################################################################|
if __name__ == '__main__':
    session = requests.Session()
    merged_df = get_bc_codes(session)
    
    if not merged_df.empty:
        # Export to CSV
        export(merged_df, 'csv', EXPORT_TABLE_MERGED, subdir='species')
        print(f"    ({merged_df.shape[0]} species)")