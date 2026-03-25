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
python3 scripts/RetrieveAllChallenges.py --contest <contest_slug> [--limit 100]
```
Outputs a clean summary table with name, slug, score, difficulty, solved status, and success rate.
Use `--raw` flag if you need the full JSON response.

### Get Challenge Details (Problem Statement)
```
python3 scripts/GetChallenge.py --contest <contest_slug> --question <question_slug>
```
Outputs the cleaned problem statement with input/output format, constraints, and sample cases.
HTML, SVG, and CSS are automatically stripped for readability.
Use `--raw` flag for filtered JSON (still excludes bulky language templates).

### List Unsolved Challenges
```
python3 scripts/GetUnsolvedChallenges.py --contest <contest_slug>
```
Returns JSON with an `unsolved` array of `{name, slug}` objects.

### Test Code (sample test cases)
```
python3 scripts/testCode.py --contest <contest_slug> --question <question_slug> --language <language> --file <path_to_code_file>
```
Submits code, **polls until compilation/testing finishes** (default 30s timeout), and displays pass/fail per test case.
Use `--timeout <seconds>` to adjust the wait time.

### Submit Code
```
python3 scripts/SubmitCode.py --contest <contest_slug> --question <question_slug> --language <language> --file <path_to_code_file> [--wait]
```
Use `--wait` to poll for judging results instead of just returning the submission ID.
Use `--timeout <seconds>` to adjust wait time (default: 60s).

### Check Submission Status
```
python3 scripts/CheckSubmission.py --contest <contest_slug> --submission-id <id>
```
Polls until judging completes and shows the final status, score, and test case results.

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--contest` | Contest slug from the URL | `codemania-v6-0-finale-datathon` |
| `--question` | Challenge slug from the URL | `real-time-rolling-features` |
| `--language` | Language identifier | `python3`, `java`, `cpp`, `javascript` |
| `--file` | Path to your solution file | `solution.py` |
| `--wait` | (SubmitCode) Wait for judging to complete | flag, no value |
| `--raw` | Output raw/filtered JSON instead of summary | flag, no value |
| `--timeout` | Max seconds to wait for async operations | `30`, `60` |

## How to find slugs

The contest and question slugs come from the HackerRank URL:
`https://www.hackerrank.com/contests/<contest_slug>/challenges/<question_slug>`

Or use `RetrieveAllChallenges.py` to list all slugs.

## Workflow

When the user asks to submit or test code:
1. Check credentials exist (create if needed)
2. Confirm `contest_slug`, `question_slug`, `language`, and the code file path
3. For testing: run `testCode.py` and show the result
4. For submitting: run `SubmitCode.py --wait` and show the submission result
5. If the user wants to find question slugs first, run `RetrieveAllChallenges.py`

## Solving Unsolved Challenges in Parallel

When the user asks to solve unsolved challenges (e.g. "solve all unsolved questions"):

### Step 1 — Discover unsolved challenges
```
cd <project_root> && python3 scripts/GetUnsolvedChallenges.py --contest <contest_slug>
```
Parse the `unsolved` array from the JSON output. Cap to a maximum of **10** challenges.

### Step 2 — Spawn parallel agents
For each unsolved challenge (up to 10), launch a subagent using the Agent tool **in parallel** (all in the same response). Each agent receives this prompt:

```
You are solving a HackerRank challenge. Project root: <project_root>

Contest: <contest_slug>
Challenge: <question_slug> (<challenge_name>)
Language: <language>

Steps:
1. Read the problem statement:
   cd <project_root> && python3 scripts/GetChallenge.py --contest <contest_slug> --question <question_slug>

2. Analyze the output carefully — identify input format, output format, constraints, and examples.

3. Write a solution to a file: <project_root>/solutions/<question_slug>.<ext>
   (Create the solutions/ directory if needed)

4. Test the solution:
   cd <project_root> && python3 scripts/testCode.py --contest <contest_slug> --question <question_slug> --language <language> --file solutions/<question_slug>.<ext>
   Review the test result. If tests fail, fix the solution and retry (max 3 attempts).

5. If tests pass, submit:
   cd <project_root> && python3 scripts/SubmitCode.py --contest <contest_slug> --question <question_slug> --language <language> --file solutions/<question_slug>.<ext> --wait

6. Report back: challenge name, submission status, score, and whether it passed.
```

### Step 3 — Summarize results
After all agents finish, collect their results and present a table:

| Challenge | Status | Score |
|-----------|--------|-------|
| ...       | ...    | ...   |

### Notes
- Max 10 parallel agents at once. If there are more than 10 unsolved challenges, run in batches.
- If `GetUnsolvedChallenges.py` cannot determine solved status (no solved field in API), it treats all challenges as unsolved — inform the user and ask whether to proceed.
- Each agent writes its solution to `solutions/<question_slug>.<ext>` so solutions are preserved.

## Updating Credentials

If the user gets 401/403 errors or wants to update their session:
```
python3 scripts/config.py --session "<new_session>" --csrf-token "<new_csrf_token>"
```
