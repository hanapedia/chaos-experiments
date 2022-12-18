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
@click.option('-e', '--experiment_name', 'experiment_name', required=True, type=str)
@click.option('-o', '--output_path', 'output_path', default='./localization_errors/microservice_faults_filtered/analysis_data/unique_traces.csv') 
@click.option('-i', '--include_subset', 'include_subset', is_flag=True)
def pickle_loader(experiment_name, output_path, include_subset):
    base_dir = Path(f'./results/{experiment_name}') 
    experiment_subdir = []
    for invos_dir in os.listdir(base_dir):
        experiment_subdir.append(f'{experiment_name}/{invos_dir}')

    traces_dir = Path(f'./datasets/filtered/gateway/{experiment_name}')
    trace_files = [] 
    for file in os.listdir(traces_dir):
        trace_files.append(traces_dir/file)


    traces_analysis_dict = defaultdict(dict)

    for experiment in experiment_subdir:
        invo_file = Path(f'./results/{experiment}/anomalies.pkl')
        invos = pd.DataFrame()
        with open(invo_file, 'rb') as f:
            invos = pd.concat([invos, pickle.load(f)])
        trace_ids = set(invos.loc[lambda df: df['predict'] == True]['trace_id'].values)

        trace_file = Path(f'./datasets/filtered/gateway/{experiment}.pkl')
        traces = []
        with open(trace_file, 'rb') as f:
            traces.extend(pickle.load(f))

        anomalous_traces = []
        for trace in traces:
            if trace['trace_id'] in trace_ids:
                anomalous_traces.append(trace)

        traces_analysis_dict[experiment.split('/')[-1]]['unique'] = get_unique_traces(traces, include_subset)
        traces_analysis_dict[experiment.split('/')[-1]]['anomalous'] = get_unique_traces(anomalous_traces, include_subset)

    # pprint.pprint(traces_analysis_dict)
    with open(output_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['filename','anomaly_type', 'num_unique_patterns', 'total_unique_patterns', 'num_occ', 'total_occ', 'num_unique_patterns(anomalous_traces)', 'total_unique_patterns(anomalous_traces)', 'num_occ(anomalous_traces)', 'total_occ(anomalous_traces)'])
        for filename, traces in traces_analysis_dict.items():
            filter_service = f"ts-{filename.split('_')[0]}-service"
            row = filter_invos(filename, traces, filter_service)
            writer.writerow(row)

def get_unique_traces(traces: list, include_subset: bool):
    unique_traces_list = []
    for trace in traces:
        s_t = set(trace['s_t'])
        s_t = set(list(filter(lambda x: x[0] != x[1], list(s_t))))
        for i, _s_t_dict in enumerate(unique_traces_list):
            if include_subset:
                if s_t <= _s_t_dict['pattern']:
                    _s_t_dict['occ'] += 1
                    break
                if _s_t_dict['pattern'] <= s_t:
                    _s_t_dict['occ'] += 1
                    unique_traces_list[i]['pattern'] = s_t
                    break
            else:
                if s_t == _s_t_dict['pattern']:
                    _s_t_dict['occ'] += 1
                    break
        else: 
            unique_traces_list.append(dict(pattern=s_t, occ=1))
    return unique_traces_list

            
def filter_invos(filename: str, traces: dict, filter_service: str):
    row_unique = [filename, filename.split('_')[1]]
    row_anomalous = []
    for type, patterns in traces.items():
        num_occ = 0
        total_occ = 0
        num_unique_patterns = 0
        for pattern in patterns:
            total_occ += pattern['occ']
            for s_t in pattern['pattern']:
                if filter_service in s_t:
                    num_occ += pattern['occ']
                    num_unique_patterns += 1
                    break
        if type == 'anomalous':
            row_anomalous.extend([num_unique_patterns, len(patterns), num_occ, total_occ])
        else: 
            row_unique.extend([num_unique_patterns, len(patterns), num_occ, total_occ])

    # pprint.pprint(f"{filename},total_unique_patterns: {num_unique_patterns}, total_occ: {num_occ}")
    row_unique.extend(row_anomalous)
    return row_unique

    
if __name__ == "__main__":
    pickle_loader()
