import argparse
import json
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Test code against HackerRank sample cases')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--question', required=True, help='Question/challenge slug (e.g. real-time-rolling-features)')
parser.add_argument('--language', default='python3', help='Programming language (default: python3)')
parser.add_argument('--file', required=True, help='Path to the code file to test')
args = parser.parse_args()

with open(args.file) as f:
    code = f.read()

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

test_id = compile_response['model']['id']

result = requests.get(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}/compile_tests/{test_id}',
    cookies=get_cookies(),
    headers=get_headers(),
)

print(json.dumps(result.json(), indent=2))
