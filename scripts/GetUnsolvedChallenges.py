import argparse
import json
import sys
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='List unsolved challenges in a HackerRank contest')
parser.add_argument('--contest', required=True, help='Contest slug')
parser.add_argument('--limit', type=int, default=100, help='Max challenges to fetch (default: 100)')
args = parser.parse_args()

response = requests.get(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges?&limit={args.limit}',
    cookies=get_cookies(),
    headers=get_headers(),
)

data = response.json()
models = data.get('models', [])

if not models:
    print(json.dumps({'error': 'No challenges found or unexpected response', 'raw': data}, indent=2))
    sys.exit(1)

def is_unsolved(challenge):
    for field in ('solved', 'user_solved', 'is_solved'):
        if field in challenge:
            return not challenge[field]
    status = challenge.get('status', '')
    if status:
        return status.lower() != 'solved'
    if 'solved_challenges_count' in challenge:
        return challenge['solved_challenges_count'] == 0
    return True

unsolved = [
    {'name': c.get('name', c.get('slug')), 'slug': c['slug']}
    for c in models
    if is_unsolved(c)
]

print(json.dumps({'unsolved': unsolved, 'total_challenges': len(models), 'unsolved_count': len(unsolved)}, indent=2))
