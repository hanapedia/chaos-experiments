import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/tracerca')
from tracerca import TraceRCA

import click

@click.command('Run TraceRCA')
@click.option('-p', '--path_root', 'path_root', required=True, type=str)
@click.option('-i', '--input', 'input_path', required=True, type=str)
@click.option('-o', '--output', 'output_path', required=True, type=str)
@click.option('-h', '--history', 'history_path', required=True, type=str)
@click.option('-l', '--log_file', 'log_file', required=True, type=str)
@click.option("-f", "--fisher", "fisher_threshold", default=1, type=float)
@click.option('-t', '--ad_threshold', 'ad_threshold', default=1, type=float)
@click.option("--min-support-rate", default=0.1)
@click.option("--quiet", "-q", is_flag=True)
@click.option("--k", default=100)
def run_tracerca(path_root, input_path, output_path, history_path, log_file, fisher_threshold, ad_threshold, min_support_rate, quiet, k):
    tr = TraceRCA(path_root)
    tr.tracerca(input_path, output_path, history_path, log_file, fisher_threshold, ad_threshold, min_support_rate, quiet, k)

if __name__ == "__main__":
    run_tracerca()
