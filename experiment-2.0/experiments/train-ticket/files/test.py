import pandas as pd
import click
import pickle
import pprint 
import numpy as np

@click.command('Run TraceRCA')
@click.option('-h', '--history', 'history_path', required=True, multiple=True, type=str)
def run_tracerca(history_path):
    history_df = pd.DataFrame()
    service_list = []
    for h in range(len(history_path)):
        with open(history_path[h], 'rb') as f:
            h_pkl = pickle.load(f)
            history_df = pd.concat([history_df, h_pkl])
            # history_list.extend(h_pkl)
    history = history_df.set_index(keys=['source', 'target'], drop=True).sort_index()
    pp = pprint.PrettyPrinter()
    unique_index = np.unique(history.index.values)
    for source, target in unique_index:
        service_list.append(source)
        service_list.append(target)
    pp.pprint(len(set(service_list)))

if __name__ == "__main__":
    run_tracerca()
