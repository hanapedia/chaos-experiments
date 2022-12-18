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
# Input: erroneous results csv file
# Output: topology summary csv file, topology graph pdf file
#
@click.command('See the topological graph and pagerank')
@click.option('-e', '--experiment_name', 'experiment_name', type=str)
@click.option('-er', '--error', 'error', is_flag=True)
def topology_batch_generation(experiment_name, error):
    # parent directory to save topologies
    localization_errors_dir = Path(f'./localization_errors/{experiment_name}')
    # csv file that contains experiment results
    experiment_results_csv = Path(f'./summary/{experiment_name}/{experiment_name}_results.csv')
    dir_key = 'all_topologies'
    if error:
        experiment_results_csv = localization_errors_dir / 'errors.csv'
        dir_key = 'errorneous'
    
    fault_results = {} # will be in shape of {faultname:predictions}
    with open(experiment_results_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            fault_results['_'.join(row[0:3])] = (row[3], row[7])

    for ef, (predictions, localizedat) in fault_results.items():
        name = ef
        if int(localizedat) != 1:
            name += f'({localizedat})'
        topology = Topology(name=name, loc_err=True) 

        # directories to store topology pickle
        fault_topology_dir = localization_errors_dir / dir_key / ef
        os.makedirs(fault_topology_dir, exist_ok=True)
        topo = fault_topology_dir / 'topology.pkl' 

        # parent directory to get experiment data
        fault_results_dir = Path(f'./results/{experiment_name}/{ef}')
        invo = fault_results_dir / 'anomalies.pkl'
        df = pd.DataFrame()
        with open(invo, 'rb') as invo_f:
            _df = pickle.load(invo_f)
            df = pd.concat([df, _df])

        features = fault_results_dir / 'features'
        selected_features = {}
        with open(features, 'r') as feat_f:
            selected_features = eval("".join(feat_f.readlines()))

        root_cause = [ef.split('_')[0]]
        if '+' in root_cause[0]: 
            root_cause = ef.split('_')[0].split('+')

        predictions = list(filter(None, predictions.split(',')))

        loc_err_conf = {
            'selected_features': selected_features,
            'root_cause': root_cause,
            'predictions': predictions
        }
        topology.generate_topology(df, ('source','target'), loc_err_conf=loc_err_conf)
        with open(topo, 'wb') as topo_f:
            pickle.dump(topology.topology, topo_f)

        output_csv = fault_topology_dir / f'{ef}_node_summary.csv'
        rank_and_output(topology, output_csv)
        output_figure = fault_topology_dir / f'{ef}_figure.svg'
        topology.draw(show=False, path=output_figure)

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

if __name__ == "__main__":
    topology_batch_generation()
