import argparse
import json
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Submit code to a HackerRank challenge')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--question', required=True, help='Question/challenge slug (e.g. real-time-rolling-features)')
parser.add_argument('--language', default='python3', help='Programming language (default: python3)')
parser.add_argument('--file', required=True, help='Path to the code file to submit')
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

print(json.dumps(response.json(), indent=2))
