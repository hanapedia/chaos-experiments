import math
import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/topological_analysis')
from topological_analysis import Topology

import click
import pandas as pd
import pickle
import pprint
import networkx as nx
import matplotlib.pyplot as plt
import csv
from pathlib import Path
import os
# Input: errornous results csv file
# Output: topology summary csv file, topology graph pdf file
#
@click.command('See the topological graph and pagerank')
@click.option('-e', '--experiment_name', 'experiment_name', type=str)
def run_anomaly_analysis(experiment_name):
    localization_errors_csv = Path(f'./localization_errors/{experiment_name}/errors.csv')
    # will be in shape of {faultname:predictions}
    errornous_faults = {}
    with open(localization_errors_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            errornous_faults['_'.join(row[0:3])] = row[3]

    topologies = []
    for ef, predictions in errornous_faults.items():
        topology = Topology(name=ef, loc_err=True) 

        errornous_fault_summary_dir = localization_errors_csv.parent/ 'faults' / ef
        os.makedirs(errornous_fault_summary_dir, exist_ok=True)

        errornous_fault_results_dir = Path(f'./results/{experiment_name}/{ef}')
        topo = errornous_fault_summary_dir / 'topology.pkl' 
        with open(topo, 'rb') as topo_f:
            topo_obj = pickle.load(topo_f)
        topology.set_topology(topo_obj)

        output_csv = errornous_fault_summary_dir / f'{ef}_node_summary.csv'
        output_figure = errornous_fault_summary_dir / f'{ef}_figure.svg'
        rank_and_output(topology, output_csv)
        topology.draw(show=False, path=output_figure)

        topologies.append(topology)

    output_all_figures = localization_errors_csv.parent / f'all_figures.svg'
    draw_all(topologies, output_all_figures)

def rank_and_output(topology, output_csv):
    ranked = topology.rank_nodes(order='in')
    with open(output_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['NODE SUMMARY'])
        header = ['service']
        header.extend(list(ranked[next(iter(ranked))].keys()))
        writer.writerow(header)

        for k, v in ranked.items():
            row = [k]
            row.extend(list(v.values()))
            writer.writerow(row)
        
        
        writer.writerow([])
        writer.writerow(['EDGE SUMMARY'])
        writer.writerow(['source','target', 'num_invo', 'anomalous', 'selected_features'])
        for edge in topology.topology.edges(data=True):
            anomalous = 0
            if 'anomalous' in edge[2]:
                anomalous = 1
            selected_features = ''
            if 'selected_features' in edge[2]:
                selected_features = edge[2]['selected_features']
            row = [edge[0], edge[1], edge[2]['num_invo'], anomalous, selected_features]
            writer.writerow(row)

def draw_all(topologies: list, output_all_figures):
    nrows = 5
    ncols = 6
    fig_size = [64,36]
    dpi = 160
    _, axes = plt.subplots(nrows, ncols, figsize=fig_size, dpi=dpi, layout='tight')
    for i, topology in enumerate(topologies):
        print(math.floor(i / ncols), i % ncols)
        ax = axes[math.floor(i / ncols), i % ncols]
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.set_title(topology.name)
        topology.draw(show=False, plot_opt=dict(ax=ax))
    plt.savefig(output_all_figures)


if __name__ == "__main__":
    run_anomaly_analysis()
