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

@click.command('See the topological graph and pagerank')
@click.option('-i', '--invos', 'invos', multiple=True, default=[], type=str)
@click.option('-t', '--topo', 'topo', default='', type=str)
@click.option('-o', '--output', 'output', default='./topological_analysis/topology.pkl', type=str)
@click.option('-c', '--output_csv', 'output_csv', default='./topological_analysis/output_csv.pkl', type=str)
def run_topological_analysis(output, invos, topo, output_csv):
    if not topo and not invos:
        raise Exception('Must provide either -t or -i')

    topology = Topology()

    if invos:
        df = pd.DataFrame()
        for invo in invos:
            with open(invo, 'rb') as f:
                _df = pickle.load(f)
                # _df = _df[['source', 'target']]
                df = pd.concat([df, _df])

        topology.set_df(df)
        topology.generate_topology(('source','target'))
        with open(output, "wb") as f:
            pickle.dump(topology.topology, f)

    if topo:
        with open(topo, 'rb') as f:
            topo_obj = pickle.load(f)
        topology.set_topology(topo_obj)
            
    ranked = topology.rank_nodes(order='in')
    #
    # pp = pprint.PrettyPrinter()
    # pp.pprint(topology.topology.edges())
    with open(output_csv, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(['NODE SUMMARY'])
        writer.writerow(['service', 'num_in', 'num_out', 'num_out-in', 'num_invo-in', 'num_invo-in-avg', 'num_invo-in-var', 'num_invo-out', 'num_invo-out-avg', 'num_invo-out-var'])

        for k, v in ranked.items():
            row = [k, v['num_in'], v['num_out'], v['num_out-in'], v['num_invo-in'], v['num_invo-in-avg'], v['num_invo-in-var'], v['num_invo-out'], v['num_invo-out-avg'], v['num_invo-out-var']]
            writer.writerow(row)
        
        
        writer.writerow([])
        writer.writerow(['EDGE SUMMARY'])
        writer.writerow(['source','target', 'num_invo'])
        for k, v in topology.invo_dict.items():
            row = [k[0],k[1], v] 
            writer.writerow(row)
    topology.draw()

if __name__ == "__main__":
    run_topological_analysis()
