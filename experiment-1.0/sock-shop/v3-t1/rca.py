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
node_dict = {
    "cp1-k8s-v2" : "192.168.100.114:9100",
    "cp2-k8s-v2" : "192.168.100.37:9100",
    "node1-k8s-v2" : "192.168.100.28:9100",
    "node2-k8s-v2" : "192.168.100.224:9100",
    "node3-k8s-v2" : "192.168.100.122:9100",
}

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Root cause analysis for microservices')

    parser.add_argument('--folder_path', type=str, required=False,
                        default='./rca/',
                        help='folder name to store csv file')

    parser.add_argument('--faults_name', type=str, required=True,
                        help='folder name to store csv file')
    
    parser.add_argument('--len_second', type=int, required=False,
                    default=180,
                    help='length of time series')

    parser.add_argument('--prom_url', type=str, required=False,
                    default='http://localhost:31090/api/v1/query',
                    help='url of prometheus query')

    parser.add_argument('--end_time', type=str, required=True,
                    help='time of prometheus query')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    folder_path = args.folder_path
    faults_name= args.faults_name
    len_second = args.len_second
    prom_url = args.prom_url
    end_time= args.end_time
    end_time = Convtime.convert_time_to_unix(end_time)

    rca = Microrca(node_dict=node_dict, folder_path=folder_path, len_second=len_second, prom_url=prom_url)
    rca.run(faults_name=faults_name, end_time=end_time)
