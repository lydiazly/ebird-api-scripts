"""
Functions for exporting data
"""
import pandas as pd
import csv
import json
import os
import sys

#==============================================================================|
def export(data, suffix: str, filename: str, subdir=''):
    """
    Export to CSV or JSON. Data can be str or DataFrame.
    """
    fullpath = os.path.join(subdir, filename) + f".{suffix}"
    if subdir and not os.path.isdir(subdir):
        try:
            os.makedirs(subdir)
            print(f"Directory '{subdir}' created.")
        except OSError as e:
            sys.exit(f"makedirs failed: {e}")
    
    if suffix == 'json':
        export_to_json(data, fullpath)
    elif suffix == 'csv':
        export_to_csv(data, fullpath)
    else:
        sys.exit(f"Unsupported file type {suffix}.")
    print(f"--> Exported to: {fullpath}")

#==============================================================================|
def export_to_csv(data: pd.DataFrame, fullpath: str):
    data.to_csv(fullpath, sep=',', index=False, header=True,
                quoting=csv.QUOTE_NONNUMERIC,
                lineterminator='\n',
                encoding='utf-8')

#==============================================================================|
def export_to_json(data, fullpath: str):
    if isinstance(data, list):
        json_object = json.dumps(data, indent=4)
        with open(fullpath, 'w') as f:
            f.write(json_object)
    elif isinstance(data, pd.DataFrame):
        data.to_json(fullpath, orient='records', indent=4)
    else:
        sys.exit(f"Unsupported data type {type(data)}")