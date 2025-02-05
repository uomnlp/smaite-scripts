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

load_dotenv()

def maybe_int(i):
    try:
        return int(i)
    except:
        return i


def postprocess_answer(answers, *fields, num=(1,11)):
    print(answers)
    return {
        f"{f}_{i}": next(maybe_int(k) for k, v in answers[f"{f}{i}"].items() if v) for f in fields for i in range(*num)
    }


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


def process_worker_answers(r: Dict[str, Any], answer_fields, batch_size=10):
    num = list(range(1,batch_size+1))
    worker_answers = postprocess_answer(json.loads(r['Answer.taskAnswers'])[0], *answer_fields, num=(1,batch_size+1))
    corrupt_indices = {i for i in num if bool(r[f'Input.corrupt{i}'])}
    uncorrupt_indices = {i for i in num if not bool(r[f'Input.corrupt{i}'])}
    corrupt_score = sum(worker_answers[f'rate_{i}'] for i in corrupt_indices)/len(corrupt_indices)
    uncorrupt_score = sum(worker_answers[f'rate_{i}'] for i in uncorrupt_indices)/len(uncorrupt_indices)
    return (uncorrupt_score/corrupt_score) * 10
    

@click.command()
@click.argument('infile', default=sys.stdin)
@click.option('--log-level', default='INFO')
@click.option('--answer-fields', '-af', default='rate,verdict')
@click.option("--processed-assignments", '-pa', type=click.Path(file_okay=True, dir_okay=False),
              default='processed.json')
@click.option('--bonus-threshold', '-bt', type=float, default=20)
@click.option('--bonus-value', '-bv', type=str, default="3")
@click.option('--release', is_flag=True, default=False)
@click.option('--batch-size', type=int, default=10)
@click.option('--reject', is_flag=True, default=False)
@click.option('--reject-threshold', '-rt', type=float, default=10)
@click.option('--reject-reason', type=str,
              default="Unfortunately, we had to reject your work because you have not passed our attention checks.")
@click.option('--qualify', is_flag=True, default=False)
@click.option('--dry', is_flag=True, default=False)
@click.option('--qualification-id', type=str, default=None)  # uom-factchecker (smaite)
def main(infile, log_level, answer_fields, processed_assignments, bonus_threshold, bonus_value, reject_threshold,
         release, qualify, batch_size, qualification_id,  dry, reject, reject_reason):

    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' if not release else 'https://mturk-requester.us-east-1.amazonaws.com'
    qualification_id = qualification_id or '326R1R7QBNKEROUUN5FYJ8S4IH3BXP' if not release else '37RMV253NRB0PWFY6AWN5NOUUNUL8U'

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
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
        with open(processed_assignments, 'w+') as f:
            json.dump([], f)

    answer_fields = answer_fields.split(',')
    results: List[Dict] = [d for d in pd.read_csv(infile).fillna(0).to_dict(orient='records')]
    
    with open(processed_assignments, 'r') as f:
            processed = json.load(f)

    processed_hits = set(p['assignment_id'] for p in processed)

    processed_worker_ids = set(p['worker_id'] for p in processed)

    mturk = boto3.client(
        'mturk',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='us-east-1',
        endpoint_url=endpoint_url
    )

    for r in tqdm(results):
        # if assignment id not processed already
        assignment_id = r['AssignmentId']
        worker_id = r['WorkerId']
        is_reject = False
        is_bonus = False

        if worker_id in processed_worker_ids:
            continue
        if assignment_id in processed_hits:
            continue

        qual_score = process_worker_answers(r, answer_fields, batch_size=batch_size)
        print(qual_score)
        

        if reject and qual_score < reject_threshold:
            # reject
            is_reject = True
            if not dry:
                mturk.reject_assignment(AssignmentId=r['AssignmentId'], RequesterFeedback=reject_reason)
            else:
                logger.info(f"Rejecting {assignment_id} from {worker_id}: {reject_reason}")
        else:
            if not dry:
                mturk.approve_assignment(AssignmentId=r['AssignmentId'], RequesterFeedback='thank you!')
                mturk.associate_qualification_with_worker(QualificationTypeId=qualification_id, WorkerId=worker_id,
                                                          IntegerValue=int(qual_score))
            else:
                logger.info(f"Accepting {assignment_id} from worker {worker_id}!")
                logger.info(f"Associating {qualification_id}:{int(qual_score)} with worker {worker_id}!")
        if qual_score >= bonus_threshold:
            is_bonus = True
            if not dry:
                mturk.send_bonus(
                                WorkerId=worker_id,
                                BonusAmount=bonus_value,
                                AssignmentId=assignment_id,
                                Reason='Well done! Your score qualifies you for a bonus.',
                                UniqueRequestToken=worker_id+assignment_id
                            )
            else:
                logger.info(f"Paying ${bonus_value} to worker {worker_id} for {assignment_id}!")
        processed.append({
            "assignment_id": assignment_id,
            "worker_id": worker_id,
            "qual_score": qual_score,
            "is_reject": is_reject,
            "is_bonus": is_bonus
        })

    with open(processed_assignments, 'w+') as f:
            json.dump(processed, f)

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


if __name__ == '__main__':
    main()
