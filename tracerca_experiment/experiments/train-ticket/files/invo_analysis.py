import pandas as pd
import click
import pickle
import pprint 
import os
import numpy as np
from pathlib import Path
from collections import defaultdict

@click.command('Pickle loader')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
def pickle_loader(pickle_path):
    pp = pprint.PrettyPrinter()
    pickle_files = []
    for path in pickle_path:
        path = Path(path)
        if os.path.isdir(path):
            for file in os.listdir(path):
                pickle_files.append(path/file)
        elif os.path.isfile(path):
            pickle_files.append(path)
        
    pickle_df = pd.DataFrame()
    for pickle_file in pickle_files:
        with open(pickle_file, 'rb') as f:
            pickle_df = pd.concat([pickle_df, pickle.load(f)])

    # print(pickle_df.loc[lambda df: df['predict'] == True]['trace_id'].index)
    print(pickle_df.loc[lambda df: df['predict'] == True]['http_status'])
    # print(pickle_df.loc[('gateway', 'ts-ui-dashboard')]['http_status'].values)

if __name__ == "__main__":
    pickle_loader()

