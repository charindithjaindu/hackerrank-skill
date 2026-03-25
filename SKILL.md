# HackerRank Skill

Use this skill to interact with HackerRank contests — submit code, run test cases, or list challenges.

## Credential Setup (First Time)

Before running any script, check if `config/credentials.json` exists in the project root.

If it does NOT exist:
1. Tell the user: "No HackerRank credentials found. Please provide your session cookie and CSRF token. You can find these in your browser's DevTools under Application > Cookies / Request Headers when logged into hackerrank.com."
2. Ask for `_hrank_session` cookie value
3. Ask for `x-csrf-token` header value
4. Run the setup command:
   ```
   cd <project_root> && python3 scripts/config.py --session "<session_value>" --csrf-token "<csrf_value>"
   ```
   This saves credentials to `config/credentials.json` (gitignored).

## Operations

All scripts must be run from the project root directory so that `from config import ...` resolves correctly:
```
cd <project_root> && python3 scripts/<script>.py [args]
```

### List Challenges
```
python3 scripts/RetriveAllChallenges.py --contest <contest_slug> [--limit 100]
```
Use this to discover available `question_slug` values for a contest.

### Test Code (sample test cases)
```
python3 scripts/testCode.py --contest <contest_slug> --question <question_slug> --language <language> --file <path_to_code_file>
```

### Submit Code
```
python3 scripts/SubmitCode.py --contest <contest_slug> --question <question_slug> --language <language> --file <path_to_code_file>
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--contest` | Contest slug from the URL | `codemania-v6-0-finale-datathon` |
| `--question` | Challenge slug from the URL | `real-time-rolling-features` |
| `--language` | Language identifier | `python3`, `java`, `cpp`, `javascript` |
| `--file` | Path to your solution file | `solution.py` |

## How to find slugs

The contest and question slugs come from the HackerRank URL:
`https://www.hackerrank.com/contests/<contest_slug>/challenges/<question_slug>`

## Workflow

When the user asks to submit or test code:
1. Check credentials exist (create if needed)
2. Confirm `contest_slug`, `question_slug`, `language`, and the code file path
3. For testing: run `testCode.py` and show the result
4. For submitting: run `SubmitCode.py` and show the submission ID / status
5. If the user wants to find question slugs first, run `RetriveAllChallenges.py` and list the challenge names/slugs

## Updating Credentials

If the user gets 401/403 errors or wants to update their session:
```
python3 scripts/config.py --session "<new_session>" --csrf-token "<new_csrf_token>"
```
