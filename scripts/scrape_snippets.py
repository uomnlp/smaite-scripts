import json
import sys

import click
from loguru import logger
from tqdm import tqdm
import requests


def timeout(func, args=(), kwargs=None, timeout_duration=1, default=None):
    import signal
    kwargs = kwargs or {}

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        logger.info('timed out')
        result = default
    finally:
        signal.alarm(0)

    return result


def get_website(i):
    logger.debug(i['link'])
    try:
        res = requests.get(i['link'])
    except:
        return "FETCH_ERROR"
    try:
        # logger.debug(res.content.decode('utf-8'))
        return res.content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return res.content.decode('latin-1')
        except:
            logger.info("Failed to decode!")
            return "DECODE_ERROR"
    except:
        logger.info("Failed to decode!")
        return "DECODE_ERROR"


@click.command()
@click.argument('file', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--total', type=int, default=None)
def main(file, log_level, total):
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    logger.debug(file)
    for i, line in enumerate(tqdm(file, total=total)):
        logger.debug(line)
        inpt = json.loads(line)
        for i in inpt['results'].get('items', []):
            i['full_website'] = timeout(get_website, args=(i,), timeout_duration=2, default="TIMEOUT_ERROR")
        print(json.dumps(inpt))


if __name__ == '__main__':
    main()
