import argparse
import json
import time
from config import api
from language import decide_from_challenge

parser = argparse.ArgumentParser(description='Submit code to a HackerRank challenge')
parser.add_argument('--contest', required=True, help='Contest slug')
parser.add_argument('--question', required=True, help='Question/challenge slug (e.g. real-time-rolling-features)')
parser.add_argument('--language', help='Ignored. The script reads the challenge and chooses.')
parser.add_argument('--file', required=True, help='Path to the code file to submit')
parser.add_argument('--wait', action='store_true', help='Wait for judging to complete and show results')
parser.add_argument('--timeout', type=int, default=60, help='Max seconds to wait for judging (default: 60)')
args = parser.parse_args()

language, _, report = decide_from_challenge(args.contest, args.question)
print(report)
print()

with open(args.file) as f:
    code = f.read()

response = api(
    'POST',
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}/submissions',
    json={
        'code': code,
        'language': language,
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

    result = api('GET', base_url).json()

    model = result.get('model', {})
    status = model.get('status', '')

    if status and status not in ('Processing', 'Queued', 'Compiling', 'Running'):
        break

    time.sleep(0.4)

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
