import argparse
import json
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='List all challenges in a HackerRank contest')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--limit', type=int, default=100, help='Max number of challenges to fetch (default: 100)')
args = parser.parse_args()

response = requests.get(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges?&limit={args.limit}',
    cookies=get_cookies(),
    headers=get_headers(),
)

print(json.dumps(response.json(), indent=2))
