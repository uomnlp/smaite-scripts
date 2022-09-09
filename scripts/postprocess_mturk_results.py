import json
import os.path
import random
import sys
from itertools import groupby
from typing import List, Dict

import click
import pandas as pd
from loguru import logger
from tqdm import tqdm
import requests
from unidecode import unidecode


def maybe_int(i):
    try:
        return int(i)
    except:
        return i


def postprocess_answer(answers, *fields):
    return {
        f: next(maybe_int(k) for k, v in answers[f].items() if v) for f in fields
    }


@click.command()
@click.argument('file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--answer-fields', '-af', default='rate,verdict')
@click.option('--qualified-workers-file', '-qwf', type=click.Path(file_okay=True, dir_okay=False),
              default='workers.txt')
@click.option('--qualification-threshold', '-qt', type=float, default=.5)
def main(file, log_level, answer_fields, qualified_workers_file, qualification_threshold):
    answer_fields = answer_fields.split(',')
    results: List[Dict] = [json.loads(s) for s in pd.read_csv(file).to_json(lines=True, orient='records').splitlines()]

    def key(entry):
        return tuple(entry[k] for k in entry.keys() if k.startswith('Input'))

    input_fields = tuple(k.replace("Input.", '') for k in results[0].keys() if k.startswith('Input'))
    grouped_by_input = groupby(sorted(results, key=key), key=key)
    grouped_data = []
    for i, (key, group) in enumerate(grouped_by_input):
        result = dict(zip(input_fields, key))
        result['corrupt'] = bool(result['corrupt'])
        result['answers'] = []
        for item in group:
            worker_answers = postprocess_answer(json.loads(item['Answer.taskAnswers'])[0], *answer_fields)
            worker_answers['worker_id'] = item['WorkerId']
            result['answers'].append(worker_answers)
        print(result)

    if os.path.exists(qualified_workers_file):
        with open(qualified_workers_file, 'r') as f:
            already_qualified_workers = f.read().splitlines()
    else:
        logger.debug("File doesn't exist!")
        already_qualified_workers = []
    logger.debug(already_qualified_workers)
    # get average worker accuracy on corrupted data
    worker_key = lambda x: x['WorkerId']
    grouped_by_worker = groupby(sorted(results, key=worker_key), key=worker_key)
    worker_acc = {}
    for w, group in grouped_by_worker:
        all_corrupted = [
            postprocess_answer(json.loads(item['Answer.taskAnswers'])[0], *answer_fields)['rate'] for item
            in group if item['Input.corrupt']
        ]

        worker_acc[w] = sum(all_corrupted) / len(all_corrupted)
        logger.debug(
            f"{w} had {len(all_corrupted)} corrupted questions. {worker_acc[w]} rating (vs {qualification_threshold}).")
    qualified_workers = [k for k, v in worker_acc.items() if v < qualification_threshold]
    for w in qualified_workers:
        if w in already_qualified_workers:
            logger.warning(f"{w} is already qualified!")
    with open(qualified_workers_file, 'a+') as f:
        f.write('\n'.join(qualified_workers)+"\n" if qualified_workers else '')

    # get average worker disagreement


if __name__ == '__main__':
    main()
