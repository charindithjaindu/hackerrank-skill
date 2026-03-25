import argparse
import json
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='List all challenges in a HackerRank contest')
parser.add_argument('--contest', required=True, help='Contest slug (e.g. codemania-v6-0-finale-datathon)')
parser.add_argument('--limit', type=int, default=100, help='Max number of challenges to fetch (default: 100)')
parser.add_argument('--raw', action='store_true', help='Output raw JSON instead of summary')
args = parser.parse_args()

response = requests.get(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges?&limit={args.limit}',
    cookies=get_cookies(),
    headers=get_headers(),
)

data = response.json()

if args.raw:
    print(json.dumps(data, indent=2))
else:
    models = data.get('models', [])
    summary = []
    for m in models:
        summary.append({
            'name': m.get('name', ''),
            'slug': m.get('slug', ''),
            'max_score': m.get('max_score', 0),
            'difficulty': m.get('difficulty_name', ''),
            'solved': m.get('solved', False),
            'success_ratio': round(m.get('success_ratio', 0) * 100, 1),
            'tags': m.get('tag_names', []),
        })

    # Sort by solved status (unsolved first), then by max_score descending
    summary.sort(key=lambda x: (x['solved'], -x['max_score']))

    print(f"Contest: {args.contest}")
    print(f"Total challenges: {len(summary)}")
    solved_count = sum(1 for s in summary if s['solved'])
    print(f"Solved: {solved_count}/{len(summary)}")
    print()
    print(f"{'Name':<60} {'Slug':<55} {'Score':>5} {'Difficulty':<8} {'Solved':<7} {'Success%':>8}")
    print('-' * 155)
    for s in summary:
        status = 'YES' if s['solved'] else 'NO'
        print(f"{s['name']:<60} {s['slug']:<55} {s['max_score']:>5} {s['difficulty']:<8} {status:<7} {s['success_ratio']:>7.1f}%")
