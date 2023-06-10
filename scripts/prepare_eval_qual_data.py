import csv
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


def chunk(seq, size):
    logger.debug(f"Chunking indices: {list(range(0, len(seq), size))}, {len(seq)}, {size}")
    res = [seq[pos:pos + size] for pos in range(0, len(seq), size)]
    logger.debug(f"Size of chunk: {len(res)}!")
    return res

@click.command()
@click.argument('file', default=sys.stdin)
@click.argument('out-file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--size', type=int, default=-1)
@click.option('--corrupt-ratio', '-cr', type=float, default=0.2)
@click.option('--max-len-article', '-ml', type=int, default=5000)
@click.option('--shuffle', '--shuf', is_flag=True, default=False)
@click.option('--batch', type=int, default=0)
@click.option('--seed', type=int, default=42)
def main(file, out_file, log_level, max_len_article, size, corrupt_ratio, shuffle, batch, seed):
    random.seed(seed)
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    logger.debug(file)
    data = load_jsonl(file)
    logger.debug(f"There are {len(data)} data points!")
    if max_len_article:
        data = [d for d in data if len(d['text_article']) <= max_len_article]
    if shuffle:
        random.shuffle(data)
    data, rest = data[:size], data[:size]
    if corrupt_ratio * len(data) < 2 * len(rest):
        target = rest
    else:
        target = data
    if batch <= 0:
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
                new_d['text'] = random.choice(target)['text_article']
                new_d['corrupt'] = 'yes'
            for k, v in new_d.items():
                new_d[k] = unidecode(v).strip().replace('\n', '<br />')
            new_data.append(new_d)
    else:
        logger.debug("Batching mode!")
        num_samples_to_corrupt = int(corrupt_ratio * batch)
        logger.debug(f"Will corrupt {num_samples_to_corrupt} examples per batch!")
        new_data = []
        chunked_data = [c for c in chunk(data, batch) if len(c) == batch]
        logger.debug(f"Got {len(chunked_data)} chunks!")
        for c in chunked_data:
            corr_indices = set(random.sample(range(len(c)), num_samples_to_corrupt))
            new_d = {}
            for i, d in enumerate(c, 1):
                new_d.update({
                    f'claim{i}': d['text'],
                    f'text{i}': d['text_article'],
                    f'verdict{i}': d['explanation'],
                    f'corrupt{i}': ''
                })
                if i in corr_indices:
                    new_d[f'text{i}'] = random.choice(target)['text_article']
                    new_d[f'corrupt{i}'] = 'yes'
            for k, v in new_d.items():
                new_d[k] = " ".join(unidecode(v).strip().replace('\n', '<br />').replace('"',"'").split())
            new_data.append(new_d)
    logger.debug(f"Created {len(new_data)} new HITs!")
    df = pd.DataFrame(new_data, columns=new_data[0].keys())
    output = df.to_csv(out_file, index=False, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
    


if __name__ == '__main__':
    main()
