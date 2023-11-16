#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User constants
"""

# -- eBird API key --
API_KEY = ''
API_FILE = "../eBird_API_Key.txt" # If the file does not exist, read from terminal

# -- Target URLs --
BASE_URL = "https://api.ebird.org/v2"
URL_DICT = {
    'hotspot'   : BASE_URL + "/ref/hotspot/info/{location_code}",
    'species'   : BASE_URL + "/product/spplist/{region_code}",
    'taxonomy'  : BASE_URL + "/ref/taxonomy/ebird?species={speciesCode}",
    'subspecies': BASE_URL + "/ref/taxon/forms/{speciesCode}",
    'historical': BASE_URL + "/data/obs/{region_code}/historic/{y}/{m}/{d}",
    'bc'        : "https://www.birdatlas.bc.ca/bcdata/codes.jsp?lang=en&pg=species&sortorder=codes",
}