"""
Retrieves species list in a region from ebird.org and returns a csv.
"""
###############################################################################|
import pandas as pd
import sys
from io import StringIO

from .export_func import export

# -- Map the columns from taxonomy data to the merged table --
column_names_dict = {'SPECIES_CODE': '',
                     'COMMON_NAME': 'comName',
                     'SCIENTIFIC_NAME': 'sciName'}

###############################################################################|
def get_species(session, url_dict, region_code, headers, primary_key='speciesCode'):
    column_names_dict['SPECIES_CODE'] = primary_key
    print(column_names_dict) #xxx
    #-- Download species codes in a region --------------------------------|
    query_type = 'species'
    url_full = url_dict[query_type].format(region_code=region_code)
    print(f"\nDownloading species from '{url_full}' ...")
    response = session.get(url_full, headers=headers)
    if response.status_code == 200:
        data = response.json()
        species_df = pd.DataFrame(data, columns=[primary_key])
    else:
        sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    #-- Download names ----------------------------------------------------|
    query_type = 'taxonomy'
    print(f"Downloading taxonomy from '{url_dict[query_type]}' ...")
    df_names = []
    for species_code in species_df[primary_key]:
        # print(f"  {species_code}")
        url_full = url_dict[query_type].format(speciesCode=species_code)
        response = session.get(url_full, headers=headers)
        if response.status_code == 200:
            data = response.text
            cols = list(column_names_dict.keys())
            df = pd.read_csv(StringIO(data), usecols=cols)[cols].rename(columns=column_names_dict)
            df_names.append(df)
        else:
            sys.exit(f"GET request failed.\nURL: {url_full}\nStatus code: {response.status_code}")
    
    species_df = pd.concat(df_names, axis=0)
    return species_df

