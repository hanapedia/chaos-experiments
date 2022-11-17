import pandas as pd
import click
import pickle
import pprint 
import os
import numpy as np

@click.command('Pickle loader')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
@click.option('-s', '--show', 'show', is_flag=True)
@click.option('-d', '--is_dataframe', 'is_df', is_flag=True)
@click.option('-f', '--is_directory', 'is_dir', is_flag=True)
def pickle_loader(pickle_path, show, is_df, is_dir):
    pp = pprint.PrettyPrinter()
    if is_dir:
        pickle_files = []
        for dir in pickle_path:
            for file in os.listdir(dir):
                pickle_files.append(f'{dir}/{file}')
        pickle_path = tuple(pickle_files)
        
    if is_df:
        pickl_list = pd.DataFrame()
        for pickle_file in pickle_path:
            with open(pickle_file, 'rb') as f:
                pickl_list = pd.concat([pickl_list, pickle.load(f)])

    else:
        pickl_list = []
        for pickle_file in pickle_path:
            with open(pickle_file, 'rb') as f:
                pickl_list.extend(pickle.load(f))
    pp.pprint(len(pickl_list))
    if show:
        pp.pprint(pickl_list)

if __name__ == "__main__":
    pickle_loader()

