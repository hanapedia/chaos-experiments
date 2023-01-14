import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/microrca')
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/timezone')

import time
import argparse

from microrca import Microrca
from convtime import Convtime

# node_dict = {
#                 'cp1' : '192.168.100.254:9100',
#                 'cp2' : '192.168.100.87:9100',
#                 'node1' : '192.168.100.36:9100',
#                 'node2' : '192.168.100.210:9100',
#                 'node3' : '192.168.100.43:9100',
#         }
# node_dict = {
#     "cp1-k8s-v2" : "192.168.100.114:9100",
#     "cp2-k8s-v2" : "192.168.100.37:9100",
#     "node1-k8s-v2" : "192.168.100.28:9100",
#     "node2-k8s-v2" : "192.168.100.224:9100",
#     "node3-k8s-v2" : "192.168.100.122:9100",
# }
node_dict = {
"home-cluster-cp1":"192.168.100.33:9100",
"home-cluster-cp2":"192.168.100.180:9100",
"home-cluster-node1":"192.168.100.226:9100",
"home-cluster-node2":"192.168.100.207:9100",
"home-cluster-node3":"192.168.100.223:9100",
}

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Root cause analysis for microservices')

    parser.add_argument('--folder_path', type=str, required=False,
                        default='./rca/',
                        help='folder name to store csv file')

    parser.add_argument('--results_csv', type=str, required=False,
                        default='./rca_results.csv',
                        help='csv filename to store all the results')

    parser.add_argument('--faults_name', type=str, required=True,
                        help='folder name to store csv file')
    
    parser.add_argument('--len_second', type=int, required=False,
                        default=180,
                        help='length of time series')

    parser.add_argument('--ad_threshold', type=float, required=False,
                        default=0.05,
                        help='anomaly detection threshold')

    parser.add_argument('--alpha', type=float, required=False,
                        default=0.55,
                        help='default weight for anomalous connection')

    parser.add_argument('--prom_url', type=str, required=False,
                        default='http://localhost:31090/api/v1/query',
                        help='url of prometheus query')

    parser.add_argument('--end_time', type=str, required=False,
                        default='',
                        help='time of prometheus query')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    folder_path = args.folder_path
    results_csv = args.results_csv
    faults_name= args.faults_name
    len_second = args.len_second
    ad_threshold = args.ad_threshold
    alpha = args.alpha
    prom_url = args.prom_url
    end_time = args.end_time
    if end_time != '':
        end_time = Convtime.convert_time_to_unix(end_time)
    else:
        end_time = time.time()

    rca = Microrca(node_dict=node_dict, folder_path=folder_path, len_second=len_second, ad_threshold=ad_threshold, alpha=alpha, prom_url=prom_url)
    rca.run(faults_name=faults_name, end_time=end_time, results_csv=results_csv)
