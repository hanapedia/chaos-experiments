import pandas as pd
import click
import pickle
import pprint 
import os
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict

# Want: 
    # number of trace patterns passing through the root cause service and thier occurance
    # total number of trace patterns and total number of occurance
    # number of anomalous traces passing through the root cause service and their occurance
        # get anomalous traces from anomalies.pkl

@click.command('Trace analysis')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
@click.option('-o', '--output_path', 'output_path', default='./localization_errors/microservice_faults_filtered/analysis_data/unique_traces.csv') 
@click.option('-i', '--include_subset', 'include_subset', is_flag=True)
@click.option('-s', '--self_filter', 'self_filter', is_flag=True)
@click.option('-f', '--filter_service', 'filter_service', default='', type=str)
def pickle_loader(pickle_path, output_path, include_subset, self_filter, filter_service):

    pp = pprint.PrettyPrinter()
    pickle_files = []
    for path in pickle_path:
        path = Path(path)
        if os.path.isdir(path):
            for file in os.listdir(path):
                pickle_files.append(f'{path}/{file}')
        elif os.path.isfile(path):
            pickle_files.append(path)

    traces_dict = defaultdict(list)
    for pickle_file in pickle_files:
        pickle_path = Path(pickle_file)
        with open(pickle_path, 'rb') as f:
            traces_dict[pickle_path.name.split('.')[0]].extend(pickle.load(f))
            
    unique_traces_dict = defaultdict(list)
    for filename, traces in traces_dict.items():
        for trace in traces:
            s_t = set(trace['s_t'])
            s_t = set(list(filter(lambda x: x[0] != x[1], list(s_t))))
            for i, _s_t_dict in enumerate(unique_traces_dict[filename]):
                if include_subset:
                    if s_t <= _s_t_dict['pattern']:
                        _s_t_dict['occ'] += 1
                        break
                    if _s_t_dict['pattern'] <= s_t:
                        _s_t_dict['occ'] += 1
                        unique_traces_dict[filename][i]['pattern'] = s_t
                        break
                else:
                    if s_t == _s_t_dict['pattern']:
                        _s_t_dict['occ'] += 1
                        break
            else: 
                unique_traces_dict[filename].append(dict(pattern=s_t, occ=1))

    if filter_service or self_filter:
        with open(output_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['filename','anomaly_type', 'num_unique_patterns', 'total_unique_patterns', 'num_occ', 'total_occ'])
            for filename, traces in unique_traces_dict.items():
                if self_filter:
                    filter_service = f"ts-{filename.split('_')[0]}-service"
                row = filter_invos(filename, traces, filter_service)
                writer.writerow(row)
            
    else:
        pp.pprint(unique_traces_dict)

def filter_invos(filename: str, traces: list, filter_service: str):
    num_occ = 0
    total_occ = 0
    num_unique_patterns = 0
    for trace in traces:
        total_occ += trace['occ']
        for s_t in trace['pattern']:
            if filter_service in s_t:
                num_occ += trace['occ']
                num_unique_patterns += 1
                pprint.pprint(trace['pattern'])
                break
    pprint.pprint(f"{filename},total_unique_patterns: {num_unique_patterns}, total_occ: {num_occ}")
    return [filename, filename.split('_')[1], num_unique_patterns, len(traces), num_occ, total_occ]

    
if __name__ == "__main__":
    pickle_loader()
