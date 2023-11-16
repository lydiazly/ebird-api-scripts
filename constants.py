#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User constants
"""

#-- eBird API key --
API_KEY = ''
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from terminal

#-- Target URLs --
BASE_URL = "https://api.ebird.org/v2"
URL_DICT = {
    'hotspot'   : BASE_URL + "/ref/hotspot/info/{location_code}",
    'species'   : BASE_URL + "/product/spplist/{region_code}",
    'taxonomy'  : BASE_URL + "/ref/taxonomy/ebird?species={speciesCode}",
    'subspecies': BASE_URL + "/ref/taxon/forms/{speciesCode}",
    'obs'       : BASE_URL + "/data/obs/{region_code}/historic/{y}/{m}/{d}",
    'bc'        : "https://www.birdatlas.bc.ca/bcdata/codes.jsp?lang=en&pg=species&sortorder=codes",
}

#-- Include subspecies --
# If the sublist is empty, add all subspecies
INCLUDE_SUBSPECIES = {
    'yerwar': ['audwar', 'myrwar', ],
    'rethaw': ['hrthaw1'],
}

#-- Column names of bc code and eBird code --
CODE_EBIRD = 'speciesCode' # should be the same in the historical and the merged table
CODE_BC = 'alphaCode_bc'

CODE_REF1 = 'bandingCode' # Reference 1
CODE_REF2 = 'comNameCode' # Reference 2

#-- Column names of species names --
NAME_BC = 'comName'
NAME_EBIRD = NAME_BC + '_ebird'

#-- Columns for import/export --
COLUMN_NAMES_BC = [CODE_BC, NAME_BC]
EXPORT_COLUMN_NAMES = [CODE_BC, CODE_REF1, CODE_REF2, CODE_EBIRD, NAME_BC, NAME_EBIRD]

#-- Map the columns from taxonomy data to the merged table --
COLUMN_NAME_DICT = {
    'SPECIES_CODE'   : CODE_EBIRD,
    'COM_NAME_CODES' : 'comNameCode',
    'BANDING_CODES'  : 'bandingCode',
    'SCI_NAME_CODES' : 'sciNameCode',
    'COMMON_NAME'    : 'comName',
    'SCIENTIFIC_NAME': 'sciName',
}

#-- Export files --
# filename without suffix
EXPORT_FILE = {
    # In species/
    'codes_bc'      : "species_codes_bc",
    'species_ebird' : "species_ebird_{region_code}",
    'species_merged': "species_merged_{region_code}",
    # In csv/ or json/
    'obs'       : "obs_ebird_{start_date}",
    'obs_merged': "obs_ebird_{start_date}--{end_date}",
}
