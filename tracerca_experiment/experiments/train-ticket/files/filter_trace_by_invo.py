import pandas as pd
import click
import pickle
import pprint 
import os
import numpy as np
from pathlib import Path
from collections import defaultdict
import ast

class PythonLiteralOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)

# default_arg = "[('istio-ingressgateway', 'ts-travel-plan-service'), ('ts-travel-plan-service', 'ts-route-plan-service'), ('ts-route-plan-service', 'ts-travel-service')]"
# default_arg = "[('istio-ingressgateway', 'ts-travel-service'), ('ts-travel-service', 'ts-ticketinfo-service'), ('ts-ticketinfo-service', 'ts-basic-service')]"
default_arg = "[('istio-ingressgateway', 'ts-preserve-service')]"

@click.command('Pickle loader')
@click.option('-p', '--pickle', 'pickle_path', required=True, multiple=True, type=str)
@click.option('-i', '--invo_pattern', 'invo_pattern', cls=PythonLiteralOption, default=default_arg, help='List of tuples indicating invocations to look for')
def pickle_loader(pickle_path, invo_pattern):
    pp = pprint.PrettyPrinter()
    pickle_files = []
    for path in pickle_path:
        path = Path(path)
        if os.path.isdir(path):
            for file in os.listdir(path):
                pickle_files.append(f'{path}/{file}')
        elif os.path.isfile(path):
            pickle_files.append(path)

    pickle_dict = defaultdict(list)
    for pickle_file in pickle_files:
        pickle_path = Path(pickle_file)
        with open(pickle_path, 'rb') as f:
            pickle_dict[pickle_path.name.split('.')[0]].extend(pickle.load(f))

    filtered_pickle_dict = defaultdict(list)
    for filename, traces in pickle_dict.items():
        for trace in traces:
            s_t = list(set(trace['s_t']))
            if len(s_t + invo_pattern) - len(set(s_t + invo_pattern)) == len(invo_pattern):
                filtered_pickle_dict[filename].append(trace)

    for _, traces in filtered_pickle_dict.items():
        for i, trace in enumerate(traces, 1): 
            pp.pprint(i)
            pp.pprint(trace['s_t'])

            

if __name__ == "__main__":
    pickle_loader()


