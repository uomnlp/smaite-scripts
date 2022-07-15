import json
import os
from typing import List, Tuple

import time
from loguru import logger

import click
import sys
import requests
from tqdm import tqdm
from unidecode import unidecode

KEY = os.environ['GSE_KEY']
SE_ID = os.environ['GSE_ID']


def get_hits(query, exclude=None):
    url = "https://customsearch.googleapis.com/customsearch/v1"

    params = {
        'q': query,
        'key': KEY,
        'cx': SE_ID,
    }
    if exclude:
        params['siteSearch'] = exclude
        params['siteSearchFilter'] = 'E'
    headers = {'Accept': "Application/json"}
    response = requests.request("GET", url, headers=headers, params=params)
    output = response.json()
    return output

def load_json(d):
    try:
        return json.loads(d, strict=False)
    except Exception as e:
        logger.debug("Failed for:")
        logger.debug(d)
        return json.loads(unidecode(d), strict=False)


@click.command()
@click.argument('file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--limit', default=-1)
@click.option('--timeout', default=.5)
@click.option('--claim-field', default='text')
@click.option('--verdict-field', default='cR_textualRating')
@click.option('--id-field', default='id')
@click.option('--url-field', default='cR_url')
@click.option('--total', default=None, type=int)
@click.option('--dry', default=False, is_flag=True)
def main(file, log_level, limit, timeout, claim_field, verdict_field, id_field, url_field, total, dry):
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    click.echo(f"Total: {total}", err=True)
    for i, line in enumerate(tqdm(file, total=total)):
        if i >= limit > -1:
            break
        if line:
            #logger.debug(line)
            line = json.loads(line.strip(), strict=False)
            claim = line[claim_field]
            if claim:
                if not dry:
                    results = get_hits(claim, exclude=line[url_field])
                    res = {
                        'claim': claim,
                        'url': line[url_field],
                        'results': results,
                        'verdict': line[verdict_field],
                        'id': line[id_field]
                    }
                    logger.debug(res)
                    print(json.dumps(res))
    time.sleep(timeout)


if __name__ == '__main__':
    main()
