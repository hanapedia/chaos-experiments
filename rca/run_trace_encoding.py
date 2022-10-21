import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/tracerca')
from tracerca import TraceRCA

import click

@click.command('Run trace encoding for TraceRCA')
@click.option('-p', '--path_root', 'path_root', default='.', type=str)
@click.option('-i', '--input', 'input_path', required=True, type=str)
@click.option('-o', '--output', 'output_path', required=True, type=str)
def run_tracerca(path_root, input_path, output_path):
    tr = TraceRCA(path_root)
    tr.trace_to_invo(input_path, output_path)

if __name__ == "__main__":
    run_tracerca()
