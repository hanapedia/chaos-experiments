import pandas as pd
import click
import pickle
import pprint 
import os
import numpy as np
from pathlib import Path

@click.command('Pickle loader')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
@click.option('-s', '--show', 'show', is_flag=True)
@click.option('-d', '--is_dataframe', 'is_df', is_flag=True)
def pickle_loader(pickle_path, show, is_df):
    pp = pprint.PrettyPrinter()
    pickle_files = []
    for path in pickle_path:
        path = Path(path)
        if os.path.isdir(path):
            for file in os.listdir(path):
                pickle_files.append(f'{path}/{file}')
        elif os.path.isfile(path):
            pickle_files.append(path)
        
    if is_df:
        pickl_list = pd.DataFrame()
        for pickle_file in pickle_files:
            with open(pickle_file, 'rb') as f:
                pickl_list = pd.concat([pickl_list, pickle.load(f)])

    else:
        pickl_list = []
        for pickle_file in pickle_files:
            with open(pickle_file, 'rb') as f:
                pickl_list.extend(pickle.load(f))
    pp.pprint(len(pickl_list))
    if show:
        if is_df:
            pp.pprint(pickl_list.loc[lambda df: df['source'] == 'gateway'])
        else:
            pp.pprint(pickl_list[0:4])

if __name__ == "__main__":
    pickle_loader()

