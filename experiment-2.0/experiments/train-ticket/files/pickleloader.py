import pandas as pd
import click
import pickle
import pprint 
import numpy as np

@click.command('Pickle loader')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
def pickle_loader(pickle_path):
    pickl_list = []
    for pickle_file in pickle_path:
        with open(pickle_file, 'rb') as f:
            pickl_list.extend(pickle.load(f))
    pp = pprint.PrettyPrinter()
    pp.pprint(len(pickl_list))

if __name__ == "__main__":
    pickle_loader()

