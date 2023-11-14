"""
Functions for exporting data
"""
import pandas as pd
import csv
import json
import os
import sys

#==============================================================================|
def export(data, suffix, filename, subdir='export_to_json'):
    """
    Export to CSV or JSON. Data can be str or DataFrame.
    """
    dirname = os.path.join(suffix, subdir)
    fullpath = f"{dirname}/{filename}.{suffix}"
    if not os.path.isdir(dirname):
        try:
            os.makedirs(dirname)
            print(f"Directory '{dirname}' created.")
        except OSError as e:
            sys.exit(e)
    
    if suffix == 'json':
        export_to_json(data, fullpath)
    elif suffix == 'csv':
        export_to_csv(data, fullpath)
    else:
        sys.exit(f"Unsupported file type {suffix}.")
    print(f"--> Exported to: {fullpath}")

#==============================================================================|
def export_to_csv(data, fullpath):
    if isinstance(data, pd.core.frame.DataFrame):
        data.to_csv(fullpath, sep=',', index=False, header=True,
                    quoting=csv.QUOTE_NONNUMERIC,
                    lineterminator='\n',
                    encoding='utf-8')
    else:
        sys.exit(f"Unsupported data type {type(data)}.")

#==============================================================================|
def export_to_json(data, fullpath):
    if isinstance(data, list):
        json_object = json.dumps(data, indent=4)
        with open(fullpath, 'w') as f:
            f.write(json_object)
    elif isinstance(data, pd.core.frame.DataFrame):
        data.to_json(fullpath, orient='records', indent=4)
    else:
        sys.exit(f"Unsupported data type {type(data)}.")