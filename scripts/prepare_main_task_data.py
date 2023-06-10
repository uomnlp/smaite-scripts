from collections import defaultdict
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
from handystuff.loaders import load_jsonl, write_jsonl

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
@click.argument('pred-files', nargs=-1)
@click.argument('out-file')
@click.option('--gt-file', default='test-exp.json')
@click.option('--log-level', default='DEBUG')
@click.option('--max-len-article', '-ml', type=int, default=5000)
@click.option('--min-len-article', '-minl', type=int, default=-1)
@click.option('--shuffle', '--shuf', is_flag=True, default=False)
@click.option('--batch', type=int, default=0)
@click.option('--seed', type=int, default=42)
def main(pred_files, out_file, gt_file, log_level, max_len_article,min_len_article, shuffle, batch, seed):
    random.seed(seed)
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    logger.debug(pred_files)
    all_preds = dict()
    for pred_file in pred_files:
        all_preds[pred_file] = [l['output'] for l in load_jsonl(pred_file)]
    gt = load_jsonl(gt_file)
    for k,v in all_preds.items():
        assert len(v) == len(gt), k
    results = []
    for gt, *preds in zip(tqdm(gt), *all_preds.values()):
        claim, article = gt['input'].split('\n',1)
        article = unidecode(article).strip().replace('\n', '<br />')
        gt_verdict = gt['target']
        if min_len_article <= len(article) <= max_len_article:
            pred_to_source = defaultdict(list)
            # print(preds)
            for source, pred in zip(all_preds, preds):
                if pred:
                    pred_to_source[pred].append(source)
            pred_to_source[gt_verdict].append('gt')
            for k,v in pred_to_source.items():
                results.append({"claim": claim,
                                'text': article,
                                'verdict': k,
                                'sources': ', '.join(v)})
    logger.debug(f"Created {len(results)} new HITs!")
    if shuffle:
        random.shuffle(results)
    if batch:
        for i, batched_result in enumerate(chunk(results, batch),1):
            df = pd.DataFrame(batched_result, columns=results[0].keys())
            df.to_csv(out_file.replace(".csv", f'-batch-{i}.csv'), index=False, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
    else:
        df = pd.DataFrame(results, columns=results[0].keys())
        output = df.to_csv(out_file, index=False, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\r\n')

    # data = load_jsonl(file)
    # logger.debug(f"There are {len(data)} data points!")
    # if max_len_article:
    #     data = [d for d in data if len(d['text_article']) <= max_len_article]
    # if shuffle:
    #     random.shuffle(data)
    # data, rest = data[:size], data[:size]
    # if corrupt_ratio * len(data) < 2 * len(rest):
    #     target = rest
    # else:
    #     target = data
    # num_samples_to_corrupt = int(corrupt_ratio * len(data))
    # corr_indices = set(random.sample(range(len(data)), num_samples_to_corrupt))
    # new_data = []
    # logger.debug(corr_indices)
    # for i, d in enumerate(data):
    #     new_d = {
    #         'claim': d['text'],
    #         'text': d['text_article'],
    #         'verdict': d['explanation'],
    #         'source': ''
    #     }
    #     if i in corr_indices:
    #         new_d['text'] = random.choice(target)['text_article']
    #         new_d['corrupt'] = 'yes'
    #     for k, v in new_d.items():
    #         new_d[k] = unidecode(v).strip().replace('\n', '<br />')
    #     new_data.append(new_d)
       
    # logger.debug(f"Created {len(new_data)} new HITs!")
    # df = pd.DataFrame(new_data, columns=new_data[0].keys())
    # output = df.to_csv(out_file, index=False, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
    


if __name__ == '__main__':
    main()
