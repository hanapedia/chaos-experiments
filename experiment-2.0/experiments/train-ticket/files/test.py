import pandas as pd
import click
import pickle
import pprint 
import numpy as np

@click.command('Run TraceRCA')
@click.option('-p', '--path', 'path', required=True, type=str)
def run_tracerca(path):
    selected_features = {}
    with open(path, 'r') as feat_f:
        selected_features = eval("".join(feat_f.readlines()))
    pp = pprint.PrettyPrinter()
    pp.pprint(selected_features.items())

if __name__ == "__main__":
    run_tracerca()
