#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User constants
"""
# 2023-11-15 created by Lydia
# 2023-11-17 last modified by Lydia

###############################################################################|

#-- eBird API key -------------------------------------------------------------|
# (Can be reset by cli arguments)
API_KEY = ''
# The file contains the key
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from the terminal

#-- Country, subnational1, subnational2, or location code ---------------------|
# (Can be reset by cli arguments)
# For observation data:
REGION_CODE_OBS = 'L164543' # North Vancouver--Maplewood Conservation Area
# For species list:
REGION_CODE_SPC = 'CA-BC'

#-- Target URLs ---------------------------------------------------------------|
BASE_URL = "https://api.ebird.org/v2"
URL_DICT = {
    'hotspot'   : BASE_URL + "/ref/hotspot/info/{location_code}",
    'species'   : BASE_URL + "/product/spplist/{region_code}",
    'taxa'      : BASE_URL + "/ref/taxonomy/ebird?species={speciesCode}",
    'subspecies': BASE_URL + "/ref/taxon/forms/{speciesCode}",
    'obs'       : BASE_URL + "/data/obs/{region_code}/historic/{y}/{m}/{d}",
    'bc'        : "https://www.birdatlas.bc.ca/bcdata/codes.jsp?lang=en&pg=species&sortorder=codes",
}

###############################################################################|

#-- Include subspecies --------------------------------------------------------|
# (If any sublist is empty, retrieve all subspecies of that species)
INCLUDE_SUBSPECIES = {
    'yerwar': ['audwar', 'myrwar', ],
    'rethaw': ['hrthaw1',],
}

#-- Column names in the historical data (do not change) -----------------------|
COUNT_COL  = 'howMany'
EXTRA_COLS = ['exoticCategory',] # not in every table
OBS_COLS   = ['speciesCode', 'comName', 'sciName', 'howMany']

#-- Column names of BC codes and eBird codes ----------------------------------|
# CODE_EBIRD: the 'speciesCode' from eBird historical data
# CODE_BC: the alpha/4-letter codes from BC Breeding Bird Atlas
CODE_EBIRD = 'speciesCode' # should be the same as in the historical data
CODE_BC    = 'alphaCode_bc' # can be changed

CODE_REF1 = 'bandingCode' # Code reference 1 (from eBird data)
CODE_REF2 = 'comNameCode' # Code reference 2 (from eBird data)

#-- Column names of species common/English names ------------------------------|
NAME_BC    = 'comName' # should be the same as in the historical data
NAME_EBIRD = NAME_BC + '_ebird' # can be changed

#-- Select & map the columns from taxa to the final observation table ---------|
# (Keep the order and values of the first 4 keys)
TAXA_COLUMN_DICT = {
    'SPECIES_CODE'   : CODE_EBIRD,
    'COM_NAME_CODES' : 'comNameCode',
    'BANDING_CODES'  : 'bandingCode',
    'COMMON_NAME'    : NAME_BC,
    'SCI_NAME_CODES' : 'sciNameCode',
    'SCIENTIFIC_NAME': 'sciName',
    'FAMILY_COM_NAME': 'familyComName',
    'FAMILY_SCI_NAME': 'familySciName',
    'FAMILY_CODE'    : 'familyCode',
    'ORDER'          : 'order',
}

#-- Map the columns for observation table -------------------------------------|
# (Keep empty to use the values above)
OBS_COLUMN_DICT = {}

#-- Columns for import/export species -----------------------------------------|
COMMENT_COL = 'comment'
SPC_COLS_BC     = [CODE_BC, NAME_BC]
EXPORT_SPC_COLS = [CODE_BC, CODE_REF1, CODE_REF2, CODE_EBIRD,
                   NAME_BC, NAME_EBIRD,
                   *list(TAXA_COLUMN_DICT.values())[4:],
                   COMMENT_COL]

#-- Columns for export observation data ---------------------------------------|
EXPORT_COUNT_COL = 'count'
EXPORT_OBS_COLS  = [CODE_BC, CODE_REF1, CODE_REF2, CODE_EBIRD,
                    NAME_BC, NAME_EBIRD,
                    *list(TAXA_COLUMN_DICT.values())[4:],
                    EXPORT_COUNT_COL,
                    *EXTRA_COLS,
                    COMMENT_COL]

###############################################################################|

#-- Export files --------------------------------------------------------------|
# (Suffix and parent directory will be set later)
EXPORT_FILE = {
    # In species/
    'codes_bc'      : "species_codes_bc",
    'species_ebird' : "species_ebird_{region_code}",
    'species_merged': "species_merged_{region_code}",
    
    # In csv/{year}/{month} or json/{year}/{month}
    'obs'           : "obs_ebird_{start_date}",
    
    # In csv/{year}/ or json/{year}/
    'obs_merged'    : "obs_ebird_{start_date}--{end_date}",
}

#-- Species table for import --------------------------------------------------|
# (Full path with suffix. Can be reset by cli arguments)
SPECIES_TABLE = f"species/species_merged_CA-BC.csv"
# SPECIES_TABLE = "" # Specify a modified species table
