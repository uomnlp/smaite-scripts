import json
import sys

import click
from loguru import logger
from tqdm import tqdm


@click.command()
@click.argument('file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--limit', default=-1)
def main(file, log_level, limit):
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    for i, line in enumerate(tqdm(file)):
        inpt = json.loads(line)
        logger.debug(inpt['results']['items'])

        res = {'target': inpt['title'],
               'input': '\n'.join(e['snippet'].split('...', 1)[-1].replace('\u00a0...', '') for e in inpt['results']['items']).strip()}
        print(json.dumps(res))


if __name__ == '__main__':
    main()
