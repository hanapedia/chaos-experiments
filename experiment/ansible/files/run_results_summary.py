import os
from typing import DefaultDict, List
import click
import csv
import pandas as pd
from collections import defaultdict
from pathlib import Path


@click.command("Summarize the experiment results")
@click.option("-v", "--variant_name", "variant_name", default="chc5s", type=str)
def result_summary(variant_name):
    working_dir = Path(f"./{variant_name}")
    results_dir = working_dir / "results"
    summary = defaultdict(list)

    # list out all the injections
    for results in os.listdir(results_dir):
        summary = summarize(results, results_dir, summary)

    df = pd.DataFrame.from_dict(summary)

    output = working_dir / f"{variant_name}_results_summary.csv" 
    df.to_csv(output, index=False)
    print(df)

def parse_tracerca_results(tracerca_results):
    with open(tracerca_results, "r") as f:
        headers = next(f)
        headers = ["pattern", "score", "ps", "ips", "p(a|b)", "p(b|a)", "in", "out"]

def summarize(results, results_folder, summary: DefaultDict[str,List]):
    """
    Parse microrca and tracerca results files. 
    Return dataframe with columns: rootcause, tracerca_rank, microrca_rank, tracerca_patterns, microrca_patterns, tracerca_scores, microrca_scores
    """
    dirnameList = results.split("_")
    root_cause_service = dirnameList[0]
    summary['rootcause'].append(root_cause_service)

    tracerca_results_file = results_folder / results / "tracerca" / "results.log"
    summary = tracerca_summary(root_cause_service, tracerca_results_file, summary)

    microrca_results_file = results_folder / results / "microrca" / "results.csv"
    summary = microrca_summary(root_cause_service, microrca_results_file, summary)

    return summary

def tracerca_summary(root_cause_service, results_file, summary: DefaultDict[str, List]):
    """
    Parse tracerca result into dict of lists
    """
    if len(root_cause_service.split("+")) > 1:
        # ignore multi root cause injections
        return summary

    patterns = ''
    scores = ''
    pattern_idx = 5
    score_idx = 4
    ranking = list()
    rank = -1
    with open(results_file, "r") as f:
        _ = next(f)
        for line in f:
            line = line.strip()
            line_el = line.split("|")
            line_el = [l.strip() for l in line_el]

            if float(line_el[score_idx]) >= 0:
                patterns += f"{line_el[pattern_idx]},"
                scores += f"{line_el[score_idx]},"
                ranking.append(line_el[pattern_idx])

                
    if root_cause_service in ranking:
        rank = ranking.index(root_cause_service) + 1
    else:
        rank = -1

    summary['tracerca_rank'].append(rank)
    summary["tracerca_patterns"].append(patterns)
    summary["tracerca_scores"].append(scores)

    return summary

def microrca_summary(root_cause_service, results_file, summary: DefaultDict[str, List]):
    """
    Parse microrca result into dict of lists
    """
    patterns = ''
    scores = ''
    ranking = list()
    pattern_idx = 0
    score_idx = 1
    rank = -1
    with open(results_file, "r") as f:
        reader = csv.reader(f)
        anomalous_edges = next(reader)
        ranking_with_db = next(reader)
        ranking_without_db = next(reader)

        for service in ranking_without_db:
            service = service.replace("(", "")
            service = service.replace(")", "")
            service = service.replace("'", "")
            service = service.replace('"', "")
            service = service.strip()
            service = service.split(",")
            patterns += f"{service[pattern_idx]},"
            scores += f"{service[score_idx]},"
            ranking.append(service[pattern_idx])

    if root_cause_service in ranking:
        rank = ranking.index(root_cause_service) + 1
    else:
        rank = -1

    summary['microrca_rank'].append(rank)
    summary["microrca_patterns"].append(patterns)
    summary["microrca_scores"].append(scores)

    return summary

if __name__ == "__main__":
    result_summary()
