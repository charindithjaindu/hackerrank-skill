import argparse
import json
import time
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Submit code to a HackerRank challenge')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--question', required=True, help='Question/challenge slug (e.g. real-time-rolling-features)')
parser.add_argument('--language', default='python3', help='Programming language (default: python3)')
parser.add_argument('--file', required=True, help='Path to the code file to submit')
parser.add_argument('--wait', action='store_true', help='Wait for judging to complete and show results')
parser.add_argument('--timeout', type=int, default=60, help='Max seconds to wait for judging (default: 60)')
args = parser.parse_args()

with open(args.file) as f:
    code = f.read()

response = requests.post(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}/submissions',
    cookies=get_cookies(),
    headers=get_headers(),
    json={
        'code': code,
        'language': args.language,
        'contest_slug': args.contest,
    },
)

data = response.json()
model = data.get('model', data)
submission_id = model.get('id')

print(f"Submitted! ID: {submission_id}")

if not args.wait or not submission_id:
    print(json.dumps(data, indent=2))
    raise SystemExit(0)

# Poll for results
print("Waiting for judging...")
base_url = f'https://www.hackerrank.com/rest/contests/{args.contest}/submissions/{submission_id}'
start_time = time.time()

while True:
    elapsed = time.time() - start_time
    if elapsed > args.timeout:
        print(f"Timed out after {args.timeout}s. Check with: python3 scripts/CheckSubmission.py --contest {args.contest} --submission-id {submission_id}")
        raise SystemExit(1)

    result = requests.get(
        base_url,
        cookies=get_cookies(),
        headers=get_headers(),
    ).json()

    model = result.get('model', {})
    status = model.get('status', '')

    if status and status not in ('Processing', 'Queued', 'Compiling', 'Running'):
        break

    time.sleep(3)

print(f"\nStatus: {model.get('status', '?')}")
print(f"Score: {model.get('display_score', '?')}")

if model.get('testcase_message'):
    msgs = model['testcase_message']
    if isinstance(msgs, list):
        passed = sum(1 for m in msgs if m == 'Success')
        print(f"Test Cases: {passed}/{len(msgs)} passed")
    else:
        print(f"Message: {msgs}")

if model.get('status') == 'Accepted':
    print("\nAll test cases passed!")
