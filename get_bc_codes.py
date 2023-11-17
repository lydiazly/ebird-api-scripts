#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get the species codes from www.birdatlas.bc.ca, merge with eBird codes, and returns a table.
[In]
[Out] csv
[Python] 3.8
[Pkgs] pandas, beautifulsoup4
"""
# 2023-11-11 created by Lydia
# 2023-11-16 last modified by Lydia
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

#-- eBird codes table --
TABLE_EBIRD = f"species/{EXPORT_FILE['species_ebird']}.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
}
###############################################################################|
def get_bc_codes(session: requests.Session, region_code: str) -> pd.DataFrame:
    merged_df = pd.DataFrame()
    table_ebird = TABLE_EBIRD.format(region_code=region_code)
    
    print(f"Parsing HTML from {URL} ...")

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
                            code = col1.text.strip() # Extract the code from the <b> tag in the first <td>
                            name = cols[1].text.strip() # Extract the common name from the second <td>
                            # print(f"{code} -- {name}")
                            codes.append(code)
                            names.append(name)
                df = pd.DataFrame({SPC_COLS_BC[0]: codes, SPC_COLS_BC[1]: names})

                # Export to CSV
                export(df, 'csv', EXPORT_FILE['codes_bc'], subdir='species')
                print(f"    ({df.shape[0]} species)")
            
                #--------------------------------------------------------------|
                try:
                    # If ebird codes exists, read
                    ebird_df = pd.read_csv(table_ebird, sep=',', header=0,
                                           skipinitialspace=True,
                                           quoting=csv.QUOTE_NONNUMERIC,
                                           encoding='utf-8')
                    print(f"\nRead data from '{table_ebird}'.")
                    print(f"  {ebird_df.columns.to_list()}\n")
                    
                    # Rewrite names and store them temporarily for search
                    # 'A or B C', 'A/B C' --> 'A C/B C' --> two columns 'A C' and 'B C'
                    name_tmp = NAME_BC + '_tmp'
                    df[name_tmp] = df[NAME_BC] \
                        .apply(lambda x: re.sub(r'^(.+) (or|x) (.+) ([^ \(\)]+)( \([^\)]+\))?$',
                                                r'\1 \4 \2 \3 \4\5', x))
                    df[name_tmp] = df[name_tmp] \
                        .apply(lambda x: re.sub(r'^(.+)(\/)(.+) ([^ \(\)]+)( \([^\)]+\))?$',
                                                r'\1 \4\2\3 \4\5', x))
                    
                    # df[[name_tmp, name_tmp2]] = df[name_tmp].str.split('/',expand=True)
                    
                    # Copy the primary key for further sorting
                    bc_key_tmp = CODE_BC + '_tmp'
                    df[bc_key_tmp] = df[CODE_BC]
                    
                    # Merge data
                    merged_df = pd.merge(df, ebird_df, on=NAME_BC, how='outer')
                    merged_df.to_csv('tmp.csv', sep=',', index=False, header=True,
                                     quoting=csv.QUOTE_NONNUMERIC,
                                     lineterminator='\n',
                                     encoding='utf-8')
                    merged_df = merged_df.astype("string")
                    
                    # Copy names
                    merged_df[NAME_EBIRD] = merged_df[NAME_BC]
                    
                    # Add a comment column
                    merged_df[COMMENT_COL] = ''
                    
                    # export(merged_df, 'csv', 'tmp', subdir='species')
                    
                    # Find the rows without BC codes
                    cols_ebird = [col for col in ebird_df.columns if col != NAME_BC]
                    
                    # Check missing
                    missing_ids = merged_df.index[merged_df[bc_key_tmp].isna()].to_list()
                    for idx in missing_ids:
                        name_ebird = str(merged_df.loc[idx, NAME_BC]).strip()
                        # Maybe the name matches one of the '... or ...', '.../...', or '... x ... (hybrid)'
                        escaped_text = re.escape(name_ebird)
                        match_row = df[df[name_tmp].str.contains(fr"\b{escaped_text}\b", regex=True)]
                        if not match_row.empty:
                            # Copy code for sorting
                            merged_df.loc[idx, bc_key_tmp] = match_row[CODE_BC].values[0] + '0'
                            merged_df.loc[idx, COMMENT_COL] = 'Possibly related to the entry above.'
                            for name_bc in match_row[NAME_BC].to_list():
                                print(f"> No match. Possibly related:\n  {name_bc} (bc), {name_ebird} (ebird)")
                            continue
                        # Maybe the code matches one of the other codes
                        code1 = merged_df.loc[idx, CODE_REF1]
                        code2 = merged_df.loc[idx, CODE_REF2]
                        code_list = []
                        code_list.extend([code1] if not pd.isna(code1) else [])
                        code_list.extend([code2] if not pd.isna(code2) else [])
                        for code in code_list:
                            match_idx = merged_df.index[merged_df[CODE_BC] == code].to_list()
                            if match_idx:
                                if pd.isna(merged_df.loc[match_idx[0], CODE_EBIRD]):
                                    # Add values to the match
                                    merged_df.loc[match_idx[0], NAME_EBIRD] = merged_df.loc[idx, NAME_BC]
                                    merged_df.loc[match_idx[0], cols_ebird] = merged_df.loc[idx, cols_ebird]
                                    merged_df.loc[match_idx[0], COMMENT_COL] = 'At least one of the eBird codes matches the BC code. Merged.'
                                    print("> Merged tuple:\n  {}, {} (bc) -- {}, {} (ebird)"
                                          .format(merged_df.loc[match_idx[0], CODE_BC], merged_df.loc[match_idx[0], NAME_BC],
                                                  code, name_ebird))
                                else:
                                    # Copy code for sorting
                                    merged_df.loc[idx, bc_key_tmp] = str(merged_df.loc[match_idx[0], CODE_BC]) + '0'
                                    merged_df.loc[idx, COMMENT_COL] = 'At least one of the eBird codes matches the BC code above, but different taxa.'
                                    print("> No match:\n  {}, {}, {}, {} (ebird)"
                                          .format(code1, code2, merged_df.loc[idx, CODE_EBIRD], name_ebird))
                                break
                    
                    # Drop extra entries
                    # merged_df = merged_df.dropna(subset=bc_key_tmp)
                    
                    
                    # Drop duplicate columns and reset index
                    merged_df = merged_df.drop_duplicates().reset_index(drop=True)
                    
                    # Sort by BC codes, then by common names
                    merged_df = merged_df.sort_values(by=[bc_key_tmp, NAME_BC, NAME_EBIRD])[EXPORT_SPC_COLS]
                    
                    # Print missing
                    mask = merged_df[CODE_BC].isna()
                    # merged_df.loc[mask, NAME_EBIRD] = pd.NA
                    missing_bc = merged_df.loc[mask, :]
                    
                    mask = merged_df[CODE_EBIRD].isna()
                    # merged_df.loc[mask, NAME_EBIRD] = pd.NA
                    missing_ebird = merged_df.loc[mask, :]
                    
                    mask = (merged_df[NAME_BC].notna()) & (merged_df[NAME_EBIRD].notna()) \
                            & (merged_df[NAME_BC] != merged_df[NAME_EBIRD])
                    mismatch = merged_df.loc[mask, :]
                    
                    pd.set_option('display.width', 200)
                    pd.set_option('display.max_info_rows', 20)
                    pd.set_option('display.max_info_columns', 10)
                    pd.set_option('display.show_dimensions', False)
                    
                    if not missing_bc.empty:
                        print("\nMissing Bird Atlas BC codes:")
                        print(missing_bc.fillna('')[[CODE_EBIRD, NAME_BC]])
                        print(f"({missing_bc.shape[0]} entries)")
                    if not missing_ebird.empty:
                        print("\nMissing ebird codes:")
                        print(missing_ebird.fillna('')[[CODE_BC, NAME_BC]])
                        print(f"({missing_ebird.shape[0]} entries)")
                    if not mismatch.empty:
                        print("\nWith different names:")
                        print(mismatch.fillna('')[[NAME_BC, NAME_EBIRD]])
                        print(f"({missing_ebird.shape[0]} entries)")
                    pd.reset_option('display.width')
                    pd.reset_option('display.max_info_rows')
                    pd.reset_option('display.max_info_columns')
                    pd.reset_option('display.show_dimensions')
                    
                    print("\nMerged:")
                    print(f"  {merged_df.columns.to_list()}\n")
                    
                except FileNotFoundError:
                    print(f"File '{table_ebird}' is not found. Skip merging.")
    
    else:
        sys.exit(f"GET request failed. Status code: {response.status_code}")
    
    return merged_df
    
###############################################################################|
if __name__ == '__main__':
    #--------------------------------------------------------------------------|
    # Parse arguments
    #--------------------------------------------------------------------------|
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default=REGION_CODE_SPC, help='location code (default: %(default)s)')
    args = parser.parse_args()
    
    region_code = args.region
    
    session = requests.Session()
    merged_df = get_bc_codes(session, region_code)
    
    if not merged_df.empty:
        export(merged_df, 'csv',
               EXPORT_FILE['species_merged'].format(region_code=region_code),
               subdir='species')
        print(f"    ({merged_df.shape[0]} species)")