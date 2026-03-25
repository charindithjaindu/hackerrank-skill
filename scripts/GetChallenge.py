import argparse
import json
import re
import html as html_module
import requests
from config import get_cookies, get_headers

parser = argparse.ArgumentParser(description='Fetch problem statement for a HackerRank challenge')
parser.add_argument('--contest', required=True, help='Contest slug')
parser.add_argument('--question', required=True, help='Question/challenge slug')
parser.add_argument('--raw', action='store_true', help='Output raw JSON instead of cleaned text')
args = parser.parse_args()

response = requests.get(
    f'https://www.hackerrank.com/rest/contests/{args.contest}/challenges/{args.question}',
    cookies=get_cookies(),
    headers=get_headers(),
)

data = response.json()
model = data.get('model', data)

if args.raw:
    # Even in raw mode, exclude bulky template fields
    exclude_keys = [k for k in model if k.endswith('_template') or k.endswith('_template_head') or k.endswith('_template_tail')]
    filtered = {k: v for k, v in model.items() if k not in exclude_keys}
    print(json.dumps(filtered, indent=2))
else:
    def clean_html(raw_html):
        """Strip HTML/SVG/CSS from body_html and return clean text."""
        if not raw_html:
            return ''
        text = raw_html
        # Remove style tags and their content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove SVG tags and their content
        text = re.sub(r'<svg[^>]*>.*?</svg>', '', text, flags=re.DOTALL)
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        # Convert structural HTML to readable format
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'</?p[^>]*>', '\n', text)
        text = re.sub(r'<li[^>]*>', '\n- ', text)
        text = re.sub(r'</?[uo]l[^>]*>', '\n', text)
        text = re.sub(r'<h[1-6][^>]*>', '\n### ', text)
        text = re.sub(r'</h[1-6]>', '\n', text)
        text = re.sub(r'<pre[^>]*>', '\n```\n', text)
        text = re.sub(r'</pre>', '\n```\n', text)
        text = re.sub(r'<code[^>]*>', '`', text)
        text = re.sub(r'</code>', '`', text)
        text = re.sub(r'<strong[^>]*>', '**', text)
        text = re.sub(r'</strong>', '**', text)
        text = re.sub(r'<em[^>]*>', '*', text)
        text = re.sub(r'</em>', '*', text)
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Unescape HTML entities
        text = html_module.unescape(text)
        # Clean up whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    body_html = model.get('body_html', '') or ''
    problem_statement = model.get('problem_statement', '') or ''

    # Try to extract sections from body_html
    cleaned = clean_html(body_html)

    # Also use problem_statement if body is empty/short
    if len(cleaned) < 50 and problem_statement:
        cleaned = problem_statement

    print(f"Challenge: {model.get('name', 'Unknown')}")
    print(f"Slug: {model.get('slug', 'Unknown')}")
    print(f"Max Score: {model.get('max_score', '?')}")
    print(f"Difficulty: {model.get('difficulty_name', '?')}")
    print(f"Languages: {', '.join(model.get('languages', []))}")
    print(f"{'='*60}")
    print()
    print(cleaned)
