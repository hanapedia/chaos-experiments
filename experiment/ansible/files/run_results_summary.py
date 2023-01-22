import os
import click
import pickle
import csv
import pprint 
import pandas as pd
from collections import defaultdict
from pathlib import Path


@click.command("Summarize the experiment results")
@click.option("-r", "--results_folder", "results_folder_name", required=True, type=str)
def result_summary(results_folder_name):
    df = pd.DataFrame()
    results_folder = Path(f'./results/{results_folder_name}')
    for results in os.listdir(results_folder):
        summary = summarize(results, results_folder)
        df = pd.concat([df, summary])

    os.makedirs(Path(f'./summary/{results_folder_name}'), exist_ok=True)
    output = Path(f'./summary/{results_folder_name}/{results_folder_name}_results.csv')
    df = df.sort_index()
    df.to_csv(output)

    os.makedirs(Path(f'./localization_errors/{results_folder_name}'), exist_ok=True)
    error_output = Path(f'./localization_errors/{results_folder_name}/errors.csv')
    errornous = df.loc[df['localizedat'] != 1]
    errornous.to_csv(error_output)

    error_pkl = Path(f'./localization_errors/{results_folder_name}/errors.pkl')
    with open(error_pkl, "wb") as f:
        pickle.dump(errornous, f)

def summarize(results, results_folder):
    filePath = os.path.join(results_folder, results, "results.log")
    summary = defaultdict(list)
    # print(filePath)

    if not os.path.isfile(filePath):
        # print(os.path.isfile(filePath))
        dirnameList = results.split("_")
        summary['rootcause'] = [dirnameList[0]]
        summary['faulttype'] = [dirnameList[1]]
        summary['injectionver'] = [dirnameList[2]]
        summary['localizedat'] = [-1]
        df = pd.DataFrame.from_dict(summary).set_index(keys=['rootcause','faulttype','injectionver'], drop=True)
        return df

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

            # print(line_el[4])
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
    if len(dirnameList[0].split("+")) > 1:
        ans = dirnameList[0].split("+")  
        if ans[0] in ranking and ans[1] in ranking:
            rank = max(ranking.index(ans[0]) + 1, ranking.index(ans[1]) + 1)
            if rank == 2:
                rank = 1
        else:
            rank = -1
    elif dirnameList[0] in ranking:
        rank = ranking.index(dirnameList[0]) + 1
    else:
        rank = -1
    summary['localizedat'] = [rank]

    df = pd.DataFrame.from_dict(summary).set_index(keys=['rootcause','faulttype','injectionver'], drop=True)
    return df


if __name__ == "__main__":
    result_summary()
