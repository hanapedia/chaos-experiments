import click
import pandas as pd
import pickle
import pprint
import random

@click.command('See the topological graph and pagerank')
@click.option('-i', '--input', 'input', multiple=True, default=[], type=str)
@click.option('-o', '--output', 'output', default='./topological_analysis/topology.pkl', type=str)
@click.option('-f', '--filter_key', 'filter_key', default=[''], multiple=True)
@click.option('-s', '--size', 'size', default=1.0, type=float)
def run_data_set_filtering(input, output, filter_key, size):
    traces = list()
    for i in input:
        with open(i, "rb") as f:
            _trace = pickle.load(f)
            traces.extend(_trace)

    filter_key = list(filter_key)
    filtered = list()
    if filter_key[0] == '':
        for trace in traces:
            if random.random() <= size:
                filtered.append(trace)
    else:
        for trace in traces:
            for st in trace['s_t']:
                st = list(set(st))
                st.extend(filter_key)
                if len(st) != len(set(st)) and random.random() <= size:
                    filtered.append(trace)
                    break

    pp = pprint.PrettyPrinter()
    pp.pprint(filtered[0:5])
    pp.pprint(f"{len(traces)} -> {len(filtered)}")

    with open(output, "wb") as f:
        pickle.dump(filtered, f)


if __name__ == "__main__":
     run_data_set_filtering()
