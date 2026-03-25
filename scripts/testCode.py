import argparse
import json
import time
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Test code against HackerRank sample cases')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--question', required=True, help='Question/challenge slug (e.g. real-time-rolling-features)')
parser.add_argument('--language', default='python3', help='Programming language (default: python3)')
parser.add_argument('--file', required=True, help='Path to the code file to test')
parser.add_argument('--timeout', type=int, default=30, help='Max seconds to wait for results (default: 30)')
args = parser.parse_args()

with open(args.file) as f:
    code = f.read()

# Step 1: Submit code for compilation/testing
compile_response = requests.post(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}/compile_tests',
    cookies=get_cookies(),
    headers=get_headers(),
    json={
        'code': code,
        'language': args.language,
        'customtestcase': False,
    },
).json()

if 'model' not in compile_response or 'id' not in compile_response.get('model', {}):
    print(json.dumps(compile_response, indent=2))
    raise SystemExit(1)

test_id = compile_response['model']['id']
print(f"Test submitted (id: {test_id}). Polling for results...")

# Step 2: Poll for results
base_url = f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}/compile_tests/{test_id}'
start_time = time.time()
poll_interval = 2  # seconds

while True:
    elapsed = time.time() - start_time
    if elapsed > args.timeout:
        print(f"Timed out after {args.timeout}s waiting for test results.")
        raise SystemExit(1)

    result = requests.get(
        base_url,
        cookies=get_cookies(),
        headers=get_headers(),
    ).json()

    model = result.get('model', {})
    status = model.get('status', None)

    # Status codes: 0 = queued/running, 1 = compiled, 2 = done
    if status is not None and status >= 2:
        break
    # Also check if compilemessage or testcase results exist
    if model.get('expected_output') or model.get('stdout'):
        break

    time.sleep(poll_interval)

# Step 3: Display results cleanly
model = result.get('model', {})
print(f"\nStatus: {model.get('status', '?')}")

if model.get('compilemessage'):
    print(f"Compile message: {model['compilemessage']}")

expected = model.get('expected_output', [])
actual = model.get('stdout', [])
stdin = model.get('stdin', [])

if expected or actual:
    num_cases = max(len(expected), len(actual))
    all_pass = True
    for i in range(num_cases):
        exp = expected[i].strip() if i < len(expected) else '(none)'
        act = actual[i].strip() if i < len(actual) else '(none)'
        inp = stdin[i].strip() if i < len(stdin) else '(none)'
        passed = exp == act
        if not passed:
            all_pass = False
        status_str = 'PASS' if passed else 'FAIL'
        print(f"\n--- Test Case {i} [{status_str}] ---")
        print(f"Input:    {inp[:200]}")
        print(f"Expected: {exp[:200]}")
        print(f"Actual:   {act[:200]}")

    print(f"\nOverall: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
else:
    # Fallback: print raw result
    print(json.dumps(result, indent=2))
