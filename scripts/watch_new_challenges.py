import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import api

ROOT = Path(__file__).resolve().parent.parent


def list_challenges(contest):
    found = []
    offset = 0
    total = None
    while True:
        response = api(
            'GET',
            f'https://www.hackerrank.com/rest/contests/{contest}/challenges?offset={offset}&limit=100',
        )
        if response.status_code in (401, 403):
            raise PermissionError(str(response.status_code))
        response.raise_for_status()
        data = response.json()
        models = data.get('models') or []
        found.extend(models)
        total = data.get('total', len(found))
        offset += len(models)
        if not models or offset >= total:
            return found


def contest_ended(contest):
    response = api('GET', f'https://www.hackerrank.com/rest/contests/{contest}')
    if response.status_code in (401, 403):
        raise PermissionError(str(response.status_code))
    response.raise_for_status()
    model = response.json().get('model') or {}
    return bool(model.get('ended') or model.get('has_ended'))


def main():
    parser = argparse.ArgumentParser(description='Print when a contest gains a challenge')
    parser.add_argument('--contest', required=True)
    parser.add_argument('--interval', type=int, default=60)
    args = parser.parse_args()

    state_path = ROOT / 'config' / f'watch-{args.contest}.json'
    log_path = ROOT / 'config' / f'watch-{args.contest}.log'

    def log(message):
        with log_path.open('a') as handle:
            stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            handle.write(f'{stamp} {message}\n')

    if state_path.exists():
        seen = set(json.loads(state_path.read_text()).get('slugs', []))
        primed = True
    else:
        seen = set()
        primed = False

    auth_failures = 0
    while True:
        try:
            if contest_ended(args.contest):
                print(f'DONE: contest {args.contest} ended', flush=True)
                return 0
            challenges = list_challenges(args.contest)
            auth_failures = 0
            current = []
            for challenge in challenges:
                slug = challenge.get('slug')
                if not slug:
                    continue
                current.append({'slug': slug, 'name': challenge.get('name') or slug})
            slugs = {item['slug'] for item in current}
            if not primed:
                seen = slugs
                state_path.write_text(json.dumps({'slugs': sorted(seen)}, indent=2))
                log(f'baseline {len(seen)}')
                primed = True
            else:
                fresh = [item for item in current if item['slug'] not in seen]
                if fresh:
                    seen.update(item['slug'] for item in fresh)
                    state_path.write_text(json.dumps({'slugs': sorted(seen)}, indent=2))
                    payload = json.dumps({'contest': args.contest, 'new': fresh}, separators=(',', ':'))
                    print(f'ACTION_REQUIRED: {payload}', flush=True)
                    log(f'new {payload}')
                else:
                    log(f'unchanged {len(slugs)}')
        except PermissionError as exc:
            auth_failures += 1
            log(f'auth {exc}')
            if auth_failures >= 3:
                print(f'FAILED: auth expired for {args.contest}', flush=True)
                return 1
        except Exception as exc:
            log(f'error {type(exc).__name__}: {exc}')
        time.sleep(args.interval)


if __name__ == '__main__':
    sys.exit(main())
