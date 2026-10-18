_EXT = {
    'c': '.c',
    'cpp': '.cpp',
    'cpp14': '.cpp',
    'cpp20': '.cpp',
    'csharp': '.cs',
    'go': '.go',
    'java': '.java',
    'java8': '.java',
    'java15': '.java',
    'javascript': '.js',
    'kotlin': '.kt',
    'php': '.php',
    'pypy': '.py',
    'pypy3': '.py',
    'python': '.py',
    'python3': '.py',
    'ruby': '.rb',
    'rust': '.rs',
    'scala': '.scala',
    'swift': '.swift',
    'typescript': '.ts',
}


def file_extension(language):
    return _EXT.get(language, f'.{language}')


def language_report(languages):
    if isinstance(languages, str):
        langs = [part.strip() for part in languages.split(',') if part.strip()]
    else:
        langs = [lang for lang in (languages or []) if isinstance(lang, str) and lang]
    if len(langs) == 1:
        chosen, locked = langs[0], True
    else:
        chosen, locked = 'python3', False
    lines = [
        f"Language lock: {'yes' if locked else 'no'}",
        f"Use language: {chosen}",
        f"File extension: {file_extension(chosen)}",
        'Allowed: ' + (', '.join(langs) if langs else '(none)'),
    ]
    return chosen, locked, '\n'.join(lines)


def decide_from_challenge(contest, question, cookies=None, headers=None):
    from config import api
    response = api(
        'GET',
        f'https://www.hackerrank.com/rest/contests/{contest}/challenges/{question}',
    )
    response.raise_for_status()
    model = response.json().get('model') or {}
    return language_report(model.get('languages'))
