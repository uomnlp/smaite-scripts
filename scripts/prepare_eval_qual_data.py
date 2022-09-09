import json
import random
import sys

import click
import pandas as pd
from loguru import logger
from tqdm import tqdm
import requests
from unidecode import unidecode


def load_json(d):
    try:
        return json.loads(d, strict=False)
    except Exception as e:
        return json.loads(unidecode(d), strict=False)


def load_jsonl(path: str):
    with open(path) as f:
        return [load_json(d) for d in f.readlines()]


@click.command()
@click.argument('file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--size', type=int, default=-1)
@click.option('--corrupt-ratio', '--cr', type=float, default=0.2)
@click.option('--shuffle', '--shuf', is_flag=True, default=False)
@click.option('--seed', type=int, default=42)
def main(file, log_level, size, corrupt_ratio, shuffle, seed):
    random.seed(seed)
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    logger.debug(file)
    data = load_jsonl(file)
    if shuffle:
        random.shuffle(data)
    data, rest = data[:size], data[:size]
    num_samples_to_corrupt = int(corrupt_ratio * len(data))
    corr_indices = set(random.sample(range(len(data)), num_samples_to_corrupt))
    new_data = []
    logger.debug(corr_indices)
    for i, d in enumerate(data):
        new_d = {
            'claim': d['text'],
            'text': d['text_article'],
            'verdict': d['explanation'],
            'corrupt': ''
        }
        if i in corr_indices:
            if num_samples_to_corrupt < 2 * len(rest):
                target = rest
            else:
                target = data
            new_d['text'] = random.choice(target)['text_article']
            new_d['corrupt'] = 'yes'
        for k, v in new_d.items():
            new_d[k] = unidecode(v).strip().replace('\n', '<br />')
        new_data.append(new_d)

    df = pd.DataFrame(new_data, columns=new_data[0].keys())
    output = df.to_csv(index=False)
    print(output)


if __name__ == '__main__':
    main()
