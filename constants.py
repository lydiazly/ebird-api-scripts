#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User constants
"""

#-- eBird API key --
# Will be reset by cli arguments
API_KEY = ''
# The file contains the key
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from terminal

#-- Country, subnational1, subnational2, or location code ---------------------|
# Will be reset by cli arguments
# For observation data
REGION_CODE_OBS = 'L164543' # North Vancouver--Maplewood Conservation Area
# For species list
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

#-- Include subspecies --------------------------------------------------------|
# If the sublist is empty, add all subspecies
INCLUDE_SUBSPECIES = {
    'yerwar': ['audwar', 'myrwar', ],
    'rethaw': ['hrthaw1',],
}

#-- Columns in the historical data (do not change these) ----------------------|
COUNT_COL_NAME  = 'howMany'
EXTRA_COL_NAMES = ['exoticCategory',] # not in every table
OBS_COL_NAMES   = ['speciesCode', 'comName', 'sciName', 'howMany']

#-- Column names of bc code and eBird code ------------------------------------|
CODE_EBIRD = 'speciesCode' # should be the same in the historical and the merged table
CODE_BC    = 'alphaCode_bc'

CODE_REF1 = 'bandingCode' # Reference 1
CODE_REF2 = 'comNameCode' # Reference 2

#-- Column names of species names ---------------------------------------------|
NAME_BC    = 'comName'
NAME_EBIRD = NAME_BC + '_ebird'

#-- Columns for import/export species -----------------------------------------|
SPC_COL_NAMES_BC     = [CODE_BC, NAME_BC]
EXPORT_SPC_COL_NAMES = [CODE_BC, CODE_REF1, CODE_REF2, CODE_EBIRD, NAME_BC, NAME_EBIRD, 'sciName']

#-- Columns for export observation data ---------------------------------------|
EXPORT_COUNT_COL_NAME = 'count'
EXPORT_OBS_COL_NAMES  = [*EXPORT_SPC_COL_NAMES, EXPORT_COUNT_COL_NAME, *EXTRA_COL_NAMES]

#-- Select & map the columns from taxa to the final observation table -------- |
COLUMN_NAME_DICT = {
    'SPECIES_CODE'   : CODE_EBIRD,
    'COM_NAME_CODES' : 'comNameCode',
    'BANDING_CODES'  : 'bandingCode',
    'SCI_NAME_CODES' : 'sciNameCode',
    'COMMON_NAME'    : NAME_BC,
    'SCIENTIFIC_NAME': 'sciName',
}

#-- Export files --------------------------------------------------------------|
# filename without suffix
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
