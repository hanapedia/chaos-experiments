import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/topological_analysis')

import argparse
import csv

from topological_analysis import Topology

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Root cause analysis for microservices')

    parser.add_argument('--topology_name', type=str, required=True,
                        help='The name of the topology to be analyzed')

    parser.add_argument('--rca_path', type=str, required=False,
                        default='',
                        help='folder name where experiment results are saved')

    parser.add_argument('--csv_path', type=str, required=False,
                        default='',
                        help='path to the csv file')

    parser.add_argument('--hosting_node', type=bool, required=False,
                        default=False,
                        help='include hosting node for analysis')

    parser.add_argument('--hosting_node_label', type=str, required=False,
                        default='node',
                        help='keyword to match hosting nodes name')

    parser.add_argument('--result_path', type=str, required=False,
                        default='./topology_pagerank.csv',
                        help='csv file to save the results')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    topology_name = args.topology_name
    rca_path = args.rca_path
    csv_path = args.csv_path
    hosting_node = args.hosting_node
    hosting_node_label = args.hosting_node_label
    result_path = args.result_path

    topology = Topology(rca_path, csv_path, hosting_node, hosting_node_label)
    pagerank = topology.pagerank()
    sorted_pagerank = {k: v for k, v in sorted(pagerank.items(), reverse=True, key=lambda item: item[1])}
    result = [topology_name]
    for k,v in sorted_pagerank.items():
        result.append("%s: %s" % (k, v))


    with open(result_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(result)
