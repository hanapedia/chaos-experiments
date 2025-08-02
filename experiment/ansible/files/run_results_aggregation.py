import os
from typing import DefaultDict, List
import click
import pandas as pd
from collections import defaultdict
from pathlib import Path
from pprint import pprint

@click.command("Aggregate the experiment results")
def result_aggregation():
    working_dir = Path("./")
    summary = defaultdict(list)

    # list out all the injections
    for variant in os.listdir(working_dir):
        if os.path.isfile(variant):
            continue

        pprint(variant)
        summary["variant"].append(variant)
        results_file = working_dir / variant / f"{variant}_results_summary.csv"
        summary = aggregate(results_file, summary)

    df = pd.DataFrame.from_dict(summary)

    output = working_dir / "aggregated.csv" 
    df.to_csv(output, index=False)

def aggregate(results_file, summary: DefaultDict[str,List]):
    df = pd.read_csv(results_file)


    microrca_rank_col_name = "microrca_rank"
    microrca_avg_rank = df.loc[df[microrca_rank_col_name] >= 0, [microrca_rank_col_name]].mean().values[0]
    microrca_loc_fail_rate = len(df.loc[df[microrca_rank_col_name] < 0, [microrca_rank_col_name]]) / len(df)

    summary["avg. rank (microrca)"].append(microrca_avg_rank)
    summary["localization fail rate (microrca)"].append(microrca_loc_fail_rate)

    tracerca_rank_col_name = "tracerca_rank"
    tracerca_avg_rank = df.loc[df[tracerca_rank_col_name] >= 0, [tracerca_rank_col_name]].mean().values[0]
    tracerca_loc_fail_rate = len(df.loc[df[tracerca_rank_col_name] < 0, [tracerca_rank_col_name]]) / len(df)

    summary["avg. rank (tracerca)"].append(tracerca_avg_rank)
    summary["localization fail rate (tracerca)"].append(tracerca_loc_fail_rate)

    return summary

if __name__ == "__main__":
    result_aggregation()
