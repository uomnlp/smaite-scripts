import json
import os.path
import random
import sys
from itertools import groupby
from typing import Any, List, Dict

import boto3
import click
import pandas as pd
from loguru import logger
from tqdm import tqdm
import requests
from unidecode import unidecode
from urllib3.exceptions import RequestError
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()


def maybe_bool(b):
    if b == '1':
        return True
    if b == '2':
        return False
    return maybe_int(b)

def maybe_int(i):
    try:
        return int(i)
    except:
        return i


def postprocess_answer(answers, *fields, num=(1, 11)):
    print(answers)
    print([[(k,v) for k, v in answers[f"{f}{i}"].items() if v] for f in fields for i in range(*num)])
    return {
        f"{f}_{i}": next((maybe_bool(k) if len(answers[f"{f}{i}"]) == 2 else maybe_int(k) for k, v in answers[f"{f}{i}"].items() if v),-1) for f in fields for i in range(*num)
    }


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


def process_worker_answers(r: Dict[str, Any], answer_fields):
    worker_answers = postprocess_answer(
        json.loads(r["Answer.taskAnswers"])[0], *answer_fields, num=(1, 2)
    )
    return worker_answers


@click.command()
@click.argument("infile", default=sys.stdin)
@click.argument("outfile", type=str)
@click.option("--log-level", default="INFO")
@click.option("--answer-fields", "-af", default="contra-article,contra-self,rate,verdict,convince,new")
@click.option("--processed-assignments", '-pa', type=click.Path(file_okay=True, dir_okay=False),
              default='processed-main.json')
@click.option("--release", is_flag=True, default=False)
@click.option("--dry", is_flag=True, default=False)
def main(infile, outfile, processed_assignments, log_level, answer_fields, release, dry):
    endpoint_url = (
        "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
        if not release
        else "https://mturk-requester.us-east-1.amazonaws.com"
    )

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    assert AWS_ACCESS_KEY_ID, AWS_ACCESS_KEY_ID
    assert AWS_SECRET_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
    logger.remove(0)
    logger.add(sys.stderr, level=log_level)
    logger.debug(infile)

    if dry:
        path, ext = os.path.splitext(processed_assignments)
        processed_assignments = f"{path}-dry{ext}"

    if not os.path.exists(processed_assignments):
        logger.warning(f"Processed Assignments file doesn't exist: `{processed_assignments}`.")
        with open(processed_assignments, "w+") as f:
            json.dump([], f)

    answer_fields = answer_fields.split(",")
    results: List[Dict] = [d for d in pd.read_csv(infile).fillna(0).to_dict(orient="records")]

    with open(processed_assignments, "r") as f:
        processed = json.load(f)

    processed_hits = set(p["assignment_id"] for p in processed)


    mturk = boto3.client(
        "mturk",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1",
        endpoint_url=endpoint_url,
    )
    output = defaultdict(dict)
    for r in tqdm(results):
        # if assignment id not processed already
        assignment_id = r["AssignmentId"]
        worker_id = r["WorkerId"]

        if assignment_id in processed_hits:
            continue

        ans = process_worker_answers(r, answer_fields)
        ans['worker'] = worker_id
        hit_id = r['HITId']
        
        p = output[hit_id]
        if not p:
            d = {c: r[f'Input.{c}'] for c in ("claim","verdict","text",'sources')}
            d['text'] = d['text'].replace('<br />', '\n')
            d['sources'] = d['sources'].split(', ')
            d['answers'] = []
            d['hit_id'] = hit_id
            output[hit_id] = d
            p = output[hit_id]

        p['answers'].append(ans)
            
        if not dry:
                mturk.approve_assignment(AssignmentId=r["AssignmentId"], RequesterFeedback="thank you!")
        else:
                logger.info(f"Accepting {assignment_id} from worker {worker_id}!")
        
        processed.append(
            {
                "assignment_id": assignment_id,
                "hit_id": hit_id,
                "worker_id": worker_id
            }
        )
    output = [v for _, v in output.items()]
    with open(outfile, "w+") as f:
        f.write('\n'.join(json.dumps(o) for o in output))

    # with open(processed_assignments, "w+") as f:
    #     json.dump(processed, f)



    # save: assignment id, worker id, score, isBonus, isAccepted
    # assert False

    # for i, (key, group) in enumerate(grouped_by_input):
    #     result = dict(zip(input_fields, key))
    #     result['corrupt'] = bool(result['corrupt'])
    #     result['answers'] = []
    #     for item in group:
    #         worker_answers = postprocess_answer(json.loads(item['Answer.taskAnswers'])[0], *answer_fields)
    #         worker_answers['worker_id'] = item['WorkerId']
    #         result['answers'].append(worker_answers)
    #         grouped_data.append(result)
    #     print(result)

    # logger.debug(already_qualified_workers)
    # # get average worker accuracy on corrupted data
    # worker_key = lambda x: x['WorkerId']
    # grouped_by_worker = groupby(sorted(results, key=worker_key), key=worker_key)
    # worker_acc_corrupted = {}
    # worker_acc_uncorrupted = {}
    # pending_workers = []  # those that didn't have any corrupted examples but we don't want to disqualify them
    # for w, group in grouped_by_worker:
    #     group = list(group)
    #     all_corrupted = [
    #         postprocess_answer(json.loads(item['Answer.taskAnswers'])[0], *answer_fields)['rate'] for item
    #         in group if bool(item['Input.corrupt'])
    #     ]
    #     all_uncorrupted = [
    #         postprocess_answer(json.loads(item['Answer.taskAnswers'])[0], *answer_fields)['rate'] for item
    #         in group if not bool(item['Input.corrupt'])
    #     ]

    #     logger.debug(f"corrupted ratings: {all_corrupted}. uncorrupted ratings: {all_uncorrupted}.")
    #     if all_corrupted and all_uncorrupted:
    #         worker_acc_corrupted[w] = sum(all_corrupted) / len(all_corrupted)
    #         worker_acc_uncorrupted[w] = sum(all_uncorrupted) / len(all_uncorrupted)
    #         logger.debug(
    #             f"{w} had {len(all_corrupted)} corrupted questions. {worker_acc_corrupted[w]} rating (vs {qualification_threshold}).")
    #     else:
    #         pending_workers.append(w)
    #         logger.debug(f"{w} is pending!")

    # # qualify those where avg score on corrupted is lower than threshold and at least 0.5 lower than on uncorrupted.
    # qualified_workers = [k for k, v in worker_acc_corrupted.items() if
    #                      v < qualification_threshold and (v + 0.5) < worker_acc_uncorrupted[k]]
    # # disqualify non-qualified and non-pending workers
    # disqualified_workers = [k for k, v in worker_acc_corrupted.items() if
    #                         k not in qualified_workers and k not in pending_workers]

    # logger.info(f"{len(qualified_workers)} qualified.")
    # logger.info(f"{len(disqualified_workers)} disqualified.")
    # logger.info(f"{len(pending_workers)} pending.")

    # mturk = boto3.client(
    #     'mturk',
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #     region_name='us-east-1',
    #     endpoint_url=endpoint_url
    # )

    # if os.path.exists(processed_assignments):
    #     with open(processed_assignments, 'r') as f:
    #         already_processed = json.load(f)
    # else:
    #     already_processed = []

    # if approve:
    #     # reject all disqualified workers and do not grant qualification, approve otherwise
    #     logger.info("Approving hits")
    #     for d in tqdm(results):  # approve/reject
    #         correct_status = d['AssignmentStatus'] == 'Submitted'
    #         worker_did_good_job = d['WorkerId'] in qualified_workers or d['WorkerId'] in pending_workers
    #         if correct_status and (approve_all or worker_did_good_job):
    #             if d['AssignmentId'] not in already_processed:
    #                 try:
    #                     if not dry:
    #                         mturk.approve_assignment(AssignmentId=d['AssignmentId'], RequesterFeedback='thank you!')
    #                     logger.debug(f"Approving {d['AssignmentId']} ({'live' if not dry else 'dry'})")
    #                 except RequestError as e:
    #                     if "This operation can be called with a status of: Submitted" in str(e):
    #                         logger.debug(f"{d['AssignmentId']} was already approved!")
    #                 already_processed.append(d['AssignmentId'])
    #             else:
    #                 logger.debug(f"{d['AssignmentId']} was already processed!")
    # if reject and not approve_all:
    #     # reject all disqualified workers and do not grant qualification, approve otherwise
    #     logger.info("Rejecting hits")
    #     for d in tqdm(results):  # approve/reject
    #         if d['AssignmentStatus'] == 'Submitted':
    #             if d['AssignmentId'] not in already_processed:
    #                 try:
    #                     if not dry:
    #                         mturk.reject_assignment(AssignmentId=d['AssignmentId'],
    #                                                 RequesterFeedback=reject_reason)
    #                     logger.debug(f"Reject {d['AssignmentId']} ({'live' if not dry else 'dry'})")
    #                 except RequestError as e:
    #                     if "This operation can be called with a status of: Submitted" in str(e):
    #                         logger.debug(f"{d['AssignmentId']} was already approved!")
    #                 already_processed.append(d['AssignmentId'])
    #             else:
    #                 logger.debug(f"{d['AssignmentId']} was already processed!")
    # if qualify:
    #     # approve all qualified and grant qualification == 100*worker_acc
    #     logger.info("Qualifying workers")
    #     for w in tqdm(qualified_workers):  # grant qualification
    #         acc = worker_acc_corrupted[w]

    #         if not dry:
    #             mturk.associate_qualification_with_worker(QualificationTypeId=qualification_id, WorkerId=w,
    #                                                       IntegerValue=int(acc * 100))
    #         logger.debug(f"Qualifying {w} with {int(acc * 100)}! ({'live' if not dry else 'dry'})")
    # if save_workers:
    #     for w in qualified_workers:
    #         if w in already_qualified_workers:
    #             logger.warning(f"{w} is already qualified!")
    #     qualified_workers = [w for w in qualified_workers if w not in already_qualified_workers]
    #     with open(qualified_workers_file, 'a+') as f:
    #         f.write('\n'.join(qualified_workers) if qualified_workers else '')

    # # TODO: get average worker disagreement


if __name__ == "__main__":
    main()
