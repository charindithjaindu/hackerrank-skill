import argparse
import json
import time
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Check status of a HackerRank submission')
parser.add_argument('--contest', required=True, help='Contest slug')
parser.add_argument('--submission-id', required=True, help='Submission ID to check')
parser.add_argument('--timeout', type=int, default=60, help='Max seconds to wait for judging (default: 60)')
args = parser.parse_args()

base_url = f'https://www.hackerrank.com/rest/contests/{args.contest}/submissions/{args.submission_id}'
start_time = time.time()
poll_interval = 3

print(f"Checking submission {args.submission_id}...")

while True:
    elapsed = time.time() - start_time
    if elapsed > args.timeout:
        print(f"Timed out after {args.timeout}s waiting for judging.")
        raise SystemExit(1)

    result = requests.get(
        base_url,
        cookies=get_cookies(),
        headers=get_headers(),
    ).json()

    model = result.get('model', {})
    status = model.get('status', '')

    # HackerRank statuses: Processing, Accepted, Wrong Answer, Terminated due to timeout, etc.
    if status and status not in ('Processing', 'Queued', 'Compiling', 'Running'):
        break

    time.sleep(poll_interval)

# Display results
model = result.get('model', {})
print(f"\nSubmission ID: {model.get('id', '?')}")
print(f"Status: {model.get('status', '?')}")
print(f"Display Score: {model.get('display_score', '?')}")
print(f"Language: {model.get('language', '?')}")

if model.get('testcase_message'):
    msgs = model['testcase_message']
    if isinstance(msgs, list):
        passed = sum(1 for m in msgs if m == 'Success')
        print(f"Test Cases: {passed}/{len(msgs)} passed")
        for i, msg in enumerate(msgs):
            if msg != 'Success':
                print(f"  Case {i}: {msg}")
    else:
        print(f"Message: {msgs}")

if model.get('status') == 'Accepted':
    print("\nAll test cases passed!")
