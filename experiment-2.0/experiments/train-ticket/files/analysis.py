import os
import pickle
import csv
import pandas as pd
from collections import defaultdict
from pathlib import Path, PosixPath
from tqdm import tqdm
from pprint import pprint

import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/tracerca')
from trainticket_config import TrainTicketConfig

class TraceRcaAnalysis:
    def __init__(self, experiment_name, filtered_service='gateway', base_path='.', output='./summary_finalized', subset=True, multi_rc=False) -> None:
        self.experiment_name = experiment_name
        self.include_subset = subset
        self.multi_rc = multi_rc

        # prepare directory names for traces and invocations
        self.base_path = base_path
        self.traces_dir = Path(f'{base_path}/datasets/')
        self.results_dir = Path(f'{base_path}/results/')
        self.invos_dir = self.results_dir / self.experiment_name
        if filtered_service:
            self.injected_traces_dir = self.traces_dir / 'filtered' / filtered_service / self.experiment_name 
            self.historical_traces_dir = self.traces_dir / 'filtered' / filtered_service / 'historical_data'
            self.historical_invos_dir = self.results_dir / 'historical_data' / filtered_service 
        else:
            self.injected_traces_dir = self.traces_dir / 'A' / 'microservice_faults'
            self.historical_traces_dir = self.traces_dir / 'A' / 'uninjection'
            self.historical_invos_dir = self.results_dir / 'historical_data' 

        self.output_path = Path(f'{output}/{experiment_name}')

    # return a list of faults that yielded low accurate rca and save it as a pickle
    def get_low_accuracy(self):
        summary_file= Path(f'{self.base_path}/summary/{self.experiment_name}/{self.experiment_name}_results.csv')
        summary_dict = self.load_results_file(summary_file)  
        low_accuracy = []
        for fault_name, fault_data in summary_dict.items():
            if not self.multi_rc and '+' in fault_name:
                continue
            if fault_data['localizedat'] != '1':
                low_accuracy.append(fault_name)  
        with open(self.output_path / 'low_accuracy.pkl', 'wb') as la:
            pickle.dump(low_accuracy, la)
        
    # format data summary into pandas dataframe
    def format_data(self):
        # prepare file name for results csv and read it
        summary_file= Path(f'{self.base_path}/summary/{self.experiment_name}/{self.experiment_name}_results.csv')
        summary_dict = self.load_results_file(summary_file)  

        topology_df = pd.DataFrame()
        node_df = pd.DataFrame()
        # open trace and invocation pickles and map them by fault
        for fault_name, summary_data in tqdm(summary_dict.items()):
            if not self.multi_rc and '+' in fault_name: 
                continue
            data_map = self.get_fault_data_map(fault_name, summary_data)
            topology_df_row, node_df_row = self.analyze_fault(traces=data_map['traces'], invocations=data_map['invocations'], rca_result=data_map['rca_result'])
            topology_df = pd.concat([topology_df, topology_df_row])
            node_df = pd.concat([node_df, node_df_row])

        topology_df = topology_df.set_index(['root_cause_service', 'fault_type', 'fault_date'])
        node_df = node_df.set_index(['root_cause_service', 'fault_type', 'fault_date', 'node'])

        # historical data
        historical_topology_df = pd.DataFrame()
        historical_node_df = pd.DataFrame()
        data_map = self.get_historical_data_map()
        topology_df_row, node_df_row = self.analyze_fault(traces=data_map['traces'], invocations=data_map['invocations'], rca_result=data_map['rca_result'])
        historical_topology_df = pd.concat([historical_topology_df, topology_df_row])
        historical_node_df = pd.concat([historical_node_df, node_df_row])

        historical_topology_df = historical_topology_df.set_index(['root_cause_service', 'fault_type', 'fault_date'])
        historical_node_df = historical_node_df.set_index(['root_cause_service', 'fault_type', 'fault_date', 'node'])

        # write each dataframe to pickle file
        with open(self.output_path / 'topology_df.pkl', 'wb') as td:
            pickle.dump(topology_df, td)
        with open(self.output_path / 'node_df.pkl', 'wb') as nd:
            pickle.dump(node_df, nd)
        with open(self.output_path / 'historical_topology_df.pkl', 'wb') as htd:
            pickle.dump(historical_topology_df, htd)
        with open(self.output_path / 'historical_node_df.pkl', 'wb') as hnd:
            pickle.dump(historical_node_df, hnd)

        # write each dataframe to csv file
        topology_df.to_csv(self.output_path / 'topology_df.csv')
        node_df.to_csv(self.output_path / 'node_df.csv')
        historical_topology_df.to_csv(self.output_path / 'historical_topology_df.csv')
        historical_node_df.to_csv(self.output_path / 'historical_node_df.csv')

    # map data for a fault
    def get_fault_data_map(self, fault_name, summary_data):
        data_map = {}
        data_map['rca_result'] = summary_data  
        # prepare injected traces
        injected_trace_file = self.injected_traces_dir / f'{fault_name}.pkl' 
        injected_traces = self.load_pickle_file(injected_trace_file)
        # convert service names in traces to simple names
        injected_traces = self.convert_trace_names(injected_traces) 

        # prepare injected invos
        injected_invos_file = self.invos_dir / fault_name / 'anomalies.pkl'
        injected_invos = self.load_pickle_file(injected_invos_file)

        data_map['traces'] = injected_traces 
        data_map['invocations'] = injected_invos
        
        return data_map

    # map data for historical data
    def get_historical_data_map(self):
        historical_data_map = {}
        historical_data_map['rca_result'] = {}
        historical_data_map['traces'] = self.load_historical_traces(self.historical_traces_dir)
        historical_data_map['traces'] = self.convert_trace_names(historical_data_map['traces'])
        historical_data_map['invocations'] = self.load_historical_invos(self.historical_invos_dir)
        return historical_data_map

    # takes in traces, invocations, and experiment_result
    # is_hist flag indicates whether the topology is of historical data
    # tracename must be converted to simple names
    def analyze_fault(self, traces: list, invocations: list, rca_result={}):
        self.num_traces = len(traces)
        self.weight_edges = len(invocations) 

        # inti fault data vars for historical data
        self.root_cause_service = 'n/a'
        self.fault_type = 'n/a'
        self.fault_date = 'n/a'
        self.predictions = 'n/a'
        self.localizedat = 'n/a' 
        # destructure rca_result for fault data but not historical data
        if rca_result:
            self.root_cause_service = rca_result['root_cause']
            self.fault_type = rca_result['fault_type']
            self.fault_date = rca_result['fault_date']
            self.predictions = list(filter(None, rca_result['predictions'].split(',')))
            self.localizedat = rca_result['localizedat']

        # edges
        # edges_dict = defaultdict(int)
        # anomalous_edges_dict = defaultdict(int)
        self.edges_dict, self.anomalous_edges_dict, anomalous_trace_ids = self.get_edges(invocations)
        self.num_edges = len(self.edges_dict)
        self.num_anomalous_edges = len(self.anomalous_edges_dict)
        self.weight_anomalous_edges = sum(self.anomalous_edges_dict.values())

        # nodes
        self.nodes = self.get_nodes(self.edges_dict)
        self.num_nodes = len(self.nodes)

        # traces
        self.traces = traces
        self.anomalous_traces = self.get_anomalous_traces(traces, anomalous_trace_ids)
        self.num_anomalous_traces = len(self.anomalous_traces)
        self.unique_traces = self.get_unique_traces(traces)
        self.num_unique_traces = len(self.unique_traces)
        self.unique_anomalous_traces = self.get_unique_traces(self.anomalous_traces)
        self.num_unique_anomalous_traces = len(self.unique_anomalous_traces)

        topology_df_row = self.get_topology_row()
        node_df_row = self.get_nodes_row()

        return topology_df_row, node_df_row

    # takes invocations pandas dataframe
    # traces data is in the format of dictionaries
    def get_edges(self, invocations: pd.DataFrame):
        edges_dict = defaultdict(int)
        anomalous_edges_dict = defaultdict(int)
        anomalous_trace_ids = []
        for _, row in invocations.iterrows():
            source, target = row['source'], row['target']
            edges_dict[(source, target)] += 1
            # if anomlies invocation
            if 'predict' in invocations.columns and row['predict']:
                anomalous_edges_dict[(source, target)] += 1
                anomalous_trace_ids.append(row['trace_id'])
        return edges_dict, anomalous_edges_dict, anomalous_trace_ids

    # takes in list of traces 
    # returns a list of traces with simple service names
    def convert_trace_names(self, traces: list):
        ttc = TrainTicketConfig(True)
        converted_traces = []
        for trace in traces:
            new_s_t = []
            for invo in trace['s_t']:
                (_s, _t) = invo
                if invo[0] in ttc.SIMPLE_NAME_DICT:
                    _s = ttc.SIMPLE_NAME_DICT[invo[0]]
                if invo[1] in ttc.SIMPLE_NAME_DICT:
                    _t = ttc.SIMPLE_NAME_DICT[invo[1]]
                s_t = (_s, _t)
                new_s_t.append(s_t)
            trace['s_t'] = new_s_t
            converted_traces.append(trace)
        return converted_traces

    # takes in list of traces 
    # returns a list of dicts containing unique trace patterns and their occurance
    def get_anomalous_traces(self, traces: list, anomalous_trace_ids: list):
        anomalous_traces = []
        for trace in traces:
            if trace['trace_id'] in anomalous_trace_ids:
                anomalous_traces.append(trace)
        return anomalous_traces

    # takes in list of traces 
    # returns a list of dicts containing unique trace patterns and their occurance
    def get_unique_traces(self, traces: list):
        unique_traces = []
        for trace in traces:
            s_t = set(trace['s_t'])
            s_t = set(list(filter(lambda x: x[0] != x[1], list(s_t))))
            for i, _s_t_dict in enumerate(unique_traces):
                if self.include_subset:
                    if s_t <= _s_t_dict['pattern']:
                        _s_t_dict['occ'] += 1
                        break
                    if _s_t_dict['pattern'] <= s_t:
                        _s_t_dict['occ'] += 1
                        unique_traces[i]['pattern'] = s_t
                        break
                else:
                    if s_t == _s_t_dict['pattern']:
                        _s_t_dict['occ'] += 1
                        break
            else: 
                unique_traces.append(dict(pattern=s_t, occ=1))
        return unique_traces

    # takes unique traces
    # returns list of nodes
    def get_nodes(self, edges_dict: dict):
        nodes = {}
        for s_t in edges_dict.keys():
           nodes[s_t[0]] = 1
           nodes[s_t[1]] = 1
        return list(nodes.keys())

    # return pandas dataframe row for topology data
    def get_topology_row(self):
        topology_df_row = {
            'root_cause_service': [self.root_cause_service],
            'fault_type': [self.fault_type],
            'fault_date': [self.fault_date],
            'num_nodes': [self.num_nodes],
            'num_edges': [self.num_edges],
            'num_anomalous_edges': [self.num_anomalous_edges],
            'weight_edges': [self.weight_edges],
            'weight_anomalous_edges': [self.weight_anomalous_edges],
            'num_traces': [self.num_traces],
            'num_anomalous_traces': [self.num_anomalous_traces],
            'num_unique_traces': [self.num_unique_traces],
            'num_unique_anomalous_traces': [self.num_unique_anomalous_traces],
            'localizedat': [self.localizedat]
        }
        return pd.DataFrame.from_dict(topology_df_row)

    # return pandas dataframe row for node data
    def get_nodes_row(self):
        node_df_row = defaultdict(list)
        for node in self.nodes:
            # num in, num out, weigt in, weigt out
            num_all, weight_all = self.count_edges_for_node(node, self.edges_dict)
            # num anomaly in, num anomaly out, weigt anomaly in, weigt anomaly out
            num_anomalous, weight_anomalous = self.count_edges_for_node(node, self.anomalous_edges_dict)
            # num traces
            num_traces = self.count_traces_for_node(node, self.traces)
            # num anomalous traces
            num_anomalous_traces = self.count_traces_for_node(node, self.anomalous_traces)
            # num unique traces
            num_unique_traces = self.count_unique_traces_for_node(node, self.unique_traces)
            # num unique anomalous traces
            num_unique_anomalous_traces = self.count_unique_traces_for_node(node, self.unique_anomalous_traces)
            # root cause
            # ranked
            root_cause = 0
            ranked = 0
            if self.root_cause_service != 'n/a' and self.predictions != 'n/a':
                if self.root_cause_service == node:
                    root_cause = 1
                if node in self.predictions:
                    ranked = self.predictions.index(node) + 1

            node_df_row['root_cause_service'].append(self.root_cause_service)
            node_df_row['fault_type'].append(self.fault_type)
            node_df_row['fault_date'].append(self.fault_date)
            node_df_row['node'].append(node)
            node_df_row['num_in'].append(num_all[0])
            node_df_row['num_out'].append(num_all[1])
            node_df_row['weight_in'].append(weight_all[0])
            node_df_row['weight_out'].append(weight_all[1])
            node_df_row['num_anomalous_in'].append(num_anomalous[0])
            node_df_row['num_anomalous_out'].append(num_anomalous[1])
            node_df_row['weight_anomalous_in'].append(weight_anomalous[0])
            node_df_row['weight_anomalous_out'].append(weight_anomalous[1])
            node_df_row['num_traces'].append(num_traces)
            node_df_row['num_anomalous_traces'].append(num_anomalous_traces)
            node_df_row['num_unique_traces'].append(num_unique_traces)
            node_df_row['num_unique_anomalous_traces'].append(num_unique_anomalous_traces)
            node_df_row['root_cause'].append(root_cause)
            node_df_row['ranked'].append(ranked)

        return pd.DataFrame.from_dict(node_df_row)

    # takes node name as a string, and edges and their weight as a dict
    # returns num and weight of the edge to and from that node
    # returns two tuples
    def count_edges_for_node(self, node: str, edges_dict: dict):
        num_in = 0
        num_out = 0
        weight_in = 0
        weight_out = 0
        for s_t, weight in edges_dict.items():
            if node == s_t[1]:
                num_in += 1
                weight_in += weight
            elif node == s_t[0]:
                num_out += 1
                weight_out += weight
        return (num_in, num_out), (weight_in, weight_out)

    # takes node name as a string, and traces in a list
    # returns number of traces that contain that node
    def count_traces_for_node(self, node: str, traces: list):
        num_traces = 0
        for trace in traces:
            for invo in trace['s_t']:
                if node in invo:
                    num_traces += 1
                    break
        return num_traces

    # takes node name as a string, and unique traces in a list of dicts
    # returns number of unique traces that contain that node
    def count_unique_traces_for_node(self, node: str, unique_traces: list):
        num_unique_traces = 0
        for trace in unique_traces:
            for invo in trace['pattern']:
                if node in invo:
                    num_unique_traces += 1
                    break
        return num_unique_traces

    # utility function to load a pickle file 
    def load_pickle_file(self, input_file: Path):
        if type(input_file) not in (Path, PosixPath):
            raise Exception('input_dirs must be of type Path')

        with open(input_file, 'rb') as f:
            return pickle.load(f)

    # utility function to convert csv containeing results data to dict of dicts 
    def load_results_file(self, input_file: Path):
        if type(input_file) not in (Path, PosixPath):
            raise Exception('input_dirs must be of type Path')

        with open(input_file, 'r') as f:
            reader = csv.reader(f)
            fault_results = {}
            next(reader, None)
            for row in reader:
                fault_name = '_'.join(row[0:3])
                fault_results[fault_name] = dict(root_cause=row[0], fault_type=row[1], fault_date= row[2], predictions=row[3], localizedat=row[7])
        return fault_results

    # utility function to convert csv containeing results data to dict of dicts 
    def load_historical_traces(self, input_dir: Path):
        traces = []
        trace_files = self.dirs_to_files(input_dir) 
        for trace_file in trace_files:
            traces.extend(self.load_pickle_file(trace_file))
        return traces

    # utility function to convert csv containeing results data to dict of dicts 
    def load_historical_invos(self, input_dir: Path):
        invos = pd.DataFrame()
        invo_files = self.dirs_to_files(input_dir) 
        for invo_file in invo_files:
            invos = pd.concat([invos,self.load_pickle_file(invo_file)])
        return invos

    # utility function that converts list of directory names to list of files contained
    def dirs_to_files(self, input_dir: Path):
        if type(input_dir) not in (Path, PosixPath):
            raise Exception('input_dirs must be of type Path')

        pickle_files = []
        if os.path.isdir(input_dir):
            for file in os.listdir(input_dir):
                if os.path.isfile(input_dir / file):
                    pickle_files.append(input_dir / file)
        else:
            raise Exception(f'{input_dir} is not a directroy')

        return pickle_files

