import pandas as pd
import click
import pickle
import pprint 
import numpy as np
import matplotlib.pyplot as plt

@click.command('Run TraceRCA')
# @click.option('-p', '--path', 'path', required=True, type=str)
def run_tracerca():
    ncols = 3
    nrows = 10
    ax_w_unit = 9
    ax_h_unit = 7
    fig_size = [ncols*ax_w_unit,nrows*ax_h_unit]
    _, axes = plt.subplots(nrows, ncols, figsize=fig_size, layout='tight')
    plt.savefig('./test.svg')

if __name__ == "__main__":
    run_tracerca()
