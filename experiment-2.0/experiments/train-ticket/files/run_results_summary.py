import os
import click
import pickle
import csv
import pprint 
import pandas as pd
from collections import defaultdict


@click.command("Summarize the experiment results")
@click.option("-r", "--results_folder", "results_folders", required=True, multiple=True, type=str)
@click.option("-oc", "--output_csv", "output_csv", default="./summary/results.csv", type=str)
@click.option("-op", "--output_pickle", "output_pickle", default="./summary/results.pkl", type=str)
def result_summary(output_csv, output_pickle, results_folders):
    df = pd.DataFrame()
    for results_folder in results_folders:
        for results in  os.listdir(results_folder):
            summary = summarize(results, results_folder)
            df = pd.concat([df, summary])

    # df.set_index(keys=['rootcause', 'faulttype', 'injectionver'], drop=True).sort_index()
    # df.reset_index(drop=True)
    # pp = pprint.PrettyPrinter()
    # pp.pprint(df.sort_index())
    df = df.sort_index()
    with open(output_pickle, "+wb") as f:
        pickle.dump(df, f)

    df.to_csv(output_csv)

def summarize(results, results_folder):
    filePath = os.path.join(results_folder, results, "result.log")
    if not os.path.isfile(filePath):
        return pd.DataFrame()
    summary = defaultdict(list)
    ranking = list()
    keysList = list()
    summaryItems = ''
    summaryScores = ''
    summaryIn = ''
    summaryOut = ''
    with open(filePath, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            line_el = line.split("|")
            line_el = [l.strip() for l in line_el]

            if i == 0:
                keysList.extend([line_el[5],line_el[4],line_el[12],line_el[13]])
                continue

            if float(line_el[4]) > 0:
                summaryItems += "%s," % (line_el[5])
                summaryScores += "%s," % (line_el[4])
                summaryIn += "%s," % (line_el[10])
                summaryOut += "%s," % (line_el[11])
                ranking.append(line_el[5])

        summary[keysList[0]] = [summaryItems]
        summary[keysList[1]] = [summaryScores]
        summary[keysList[2]] = [summaryIn]
        summary[keysList[3]] = [summaryOut]
                
    dirnameList = results.split("_")
    summary['rootcause'] = [dirnameList[0]]
    summary['faulttype'] = [dirnameList[1]]
    summary['injectionver'] = [dirnameList[2]]
    if dirnameList[0] in ranking:
       rank = str(ranking.index(dirnameList[0]) + 1)
    else:
        rank = str(-1)
    summary['localizedat'] = [rank]

    df = pd.DataFrame.from_dict(summary).set_index(keys=['rootcause','faulttype','injectionver'], drop=True)
    return df


if __name__ == "__main__":
    result_summary()
