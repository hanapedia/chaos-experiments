import sys
sys.path.insert(0, '/Users/hirokihanada/code/src/github.com/hanapedia/rca_methods/tracerca')
from tracerca import TraceRCA

import click

@click.command('Run trace encoding for TraceRCA')
@click.option('-i', '--input', 'input_path', required=True, type=str)
@click.option('-o', '--output', 'output_path', required=True, type=str)
def run_tracerca(input_path, output_path):
    TraceRCA.trace_to_invo(input_path, output_path)

if __name__ == "__main__":
    run_tracerca()
