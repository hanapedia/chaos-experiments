import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/topological_analysis')
from topological_analysis import Topology

import click
import pandas as pd
import pickle
from pprint import pprint
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
import csv
import math
import os
from collections import defaultdict

# Input: experiment name, graph drawing group, multi_rc_faults
#   if multi_rc_faults flag is provided, faults with multiple root causes are separated and grouped on their own
# Output: topology graphs grouped by given categories svg files
@click.command('See the topological graph and pagerank')
@click.option('-e', '--experiment_name', 'experiment_name', type=str)
@click.option('-g', '--group_by', 'group_by', default='errorneous', type=str, help='errorneous(default), anomaly_type, or root_cause_service')
def run_anomaly_analysis(experiment_name, group_by):
    # argument validation
    if group_by not in ('errorneous', 'anomaly_type', 'root_cause_service'):
        raise Exception('Argument -g or --group_by must be errorneous, anomaly_type, or root_cause_service')
        
    figures_dir = Path(f'./localization_errors/{experiment_name}/figures')
    try:
        _ = figures_dir.resolve(strict=True)
    except:
        os.makedirs(figures_dir,exist_ok=True)

    all_topologies_dir = Path(f'./localization_errors/{experiment_name}/all_topologies')
    try:
        _ = all_topologies_dir.resolve(strict=True)
    except:
        raise Exception(f'directory not found: {all_topologies_dir}')
    experiment_results_csv = Path(f'./summary/{experiment_name}/{experiment_name}_results.csv')

    # will be in shape of {faultname:predictions}
    fault_results = {} # will be in shape of {faultname:{root_cause_service:list, anomaly_type:str, localizedat:str}}
    with open(experiment_results_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            root_cause_service = tuple(row[0].split('+'))
            fault_results['_'.join(row[0:3])] = {
                'root_cause_service': row[0],
                'anomaly_type': row[1],
                'errorneous': int(row[7])
            }

    # group results names by given conditions
    grouped = defaultdict(list)
    for name, attrs in fault_results.items():
        fault = dict(name=name, rank=attrs['errorneous'])
        # handle multi root cause faults
        if len(attrs['root_cause_service'].split('+')) > 1:
            grouped['multi_rc'].append(fault)
        elif group_by == 'errorneous':
            if attrs['errorneous'] != 1:
                grouped['erroneous'].append(fault)
            else:
                grouped['success'].append(fault)
        else:
            grouped[attrs[group_by]].append(fault)

    # draw graphs for each groups
    for group_key, faults in grouped.items():
        topologies = []
        for fault in faults:
            topology_pkl = all_topologies_dir / fault['name'] / 'topology.pkl' 
            with open(topology_pkl, 'rb') as f:
                topology_obj = pickle.load(f)

            if fault['rank'] != 1:
                fault['name'] += f' ({fault["rank"]})'
            topology = Topology(name=fault['name'], loc_err=True) 
            topology.set_topology(topology_obj)

            topologies.append(topology)

        grouped_figures_dir = figures_dir / group_by
        os.makedirs(grouped_figures_dir, exist_ok=True)
        output_path = grouped_figures_dir / f'{group_key}.svg'
        pprint(f'Drawing topologies for {group_key}:')
        draw_all(topologies, output_path)

def draw_all(topologies: list, output_all_figures):
    ncols = 2
    nrows = math.ceil(len(topologies)/2)
    ax_w_unit = 13
    ax_h_unit = 11
    fig_size = [ncols*ax_w_unit,nrows*ax_h_unit]
    _, axes = plt.subplots(nrows, ncols, figsize=fig_size, squeeze=False, layout='tight')
    for i, topology in enumerate(tqdm(topologies)):
        ax = axes[math.floor(i / ncols), i % ncols]
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.set_title(topology.name)
        topology.draw(show=False, plot_opt=dict(ax=ax))
    plt.savefig(output_all_figures)


if __name__ == "__main__":
    run_anomaly_analysis()
