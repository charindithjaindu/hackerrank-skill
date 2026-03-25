import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'credentials.json')
CONFIG_PATH = os.path.abspath(CONFIG_PATH)


def load_credentials():
    if not os.path.exists(CONFIG_PATH):
        print(f"No credentials found at {CONFIG_PATH}")
        print("Please run: python3 scripts/config.py --setup")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_credentials(session: str, csrf_token: str):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump({'_hrank_session': session, 'x-csrf-token': csrf_token}, f, indent=2)
    print(f"Credentials saved to {CONFIG_PATH}")


def get_cookies():
    creds = load_credentials()
    return {'_hrank_session': creds['_hrank_session']}


def get_headers():
    creds = load_credentials()
    return {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-csrf-token': creds['x-csrf-token'],
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Manage HackerRank credentials')
    parser.add_argument('--setup', action='store_true', help='Set up credentials interactively')
    parser.add_argument('--session', help='_hrank_session cookie value')
    parser.add_argument('--csrf-token', help='x-csrf-token header value')
    args = parser.parse_args()

    if args.setup or (args.session and args.csrf_token):
        session = args.session or input('Enter _hrank_session cookie: ').strip()
        csrf = args.csrf_token or input('Enter x-csrf-token: ').strip()
        save_credentials(session, csrf)
    else:
        parser.print_help()
