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
@click.option('-s', '--show', 'show', is_flag=True)
def pickle_loader(pickle_path, show):
    pp = pprint.PrettyPrinter()
    pickle_files = []
    for path in pickle_path:
        path = Path(path)
        if os.path.isdir(path):
            for file in os.listdir(path):
                pickle_files.append(f'{path}/{file}')
        elif os.path.isfile(path):
            pickle_files.append(path)
        
    else:
        trace_list = defaultdict(lambda: defaultdict(list))
        for pickle_file in pickle_files:
            pickle_path = Path(pickle_file)
            with open(pickle_path, 'rb') as f:
                trace_list[pickle_path.name.split('_')[1]][pickle_path.name].extend(pickle.load(f))

    for k,v in trace_list.items():
        for filename, val in v.items():
            # if len(val) < 500:
            pp.pprint(f"{k}-{filename}: {len(val)}")

if __name__ == "__main__":
    pickle_loader()

