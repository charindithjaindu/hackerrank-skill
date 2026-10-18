# HackerRank Skill

Use this skill to interact with HackerRank contests — list challenges, run tests, submit code, and solve questions.

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
The header reports `Language lock`, `Use language`, and `File extension`.
Use `--raw` flag for filtered JSON (still excludes bulky language templates).

### List Unsolved Challenges
```
python3 scripts/GetUnsolvedChallenges.py --contest <contest_slug>
```
Returns JSON with an `unsolved` array of `{name, slug}` objects.

### Test Code (sample test cases)
```
python3 scripts/testCode.py --contest <contest_slug> --question <question_slug> --file <path_to_code_file>
```
Reads the challenge, chooses the language, then polls until compilation/testing finishes (default 30s timeout) and displays pass/fail per test case.
Use `--timeout <seconds>` to adjust the wait time.

### Submit Code
```
python3 scripts/SubmitCode.py --contest <contest_slug> --question <question_slug> --file <path_to_code_file> [--wait]
```
Reads the challenge and chooses the language before submitting.
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
| `--contest` | Contest slug from the URL | |
| `--question` | Challenge slug from the URL | |
| `--language` | Ignored. Test and submit choose from the challenge. | |
| `--file` | Path to your solution file | `solution.py` |
| `--wait` | (SubmitCode) Wait for judging to complete | flag, no value |
| `--raw` | Output raw/filtered JSON instead of summary | flag, no value |
| `--timeout` | Max seconds to wait for async operations | `30`, `60` |

## How to find slugs

The contest and question slugs come from the HackerRank URL:
`https://www.hackerrank.com/contests/<contest_slug>/challenges/<question_slug>`

Or use `RetrieveAllChallenges.py` to list all slugs.

## Solution style

`GetChallenge.py` prints `Language lock`, `Use language`, and `File extension`. Test and submit make the same choice. Write `solutions/<question_slug>` plus that file extension.

- `Language lock: no`: write Python 3.
- `Language lock: yes`: write only `Use language`.

Write the file the way a person writes a contest solution. No comments, docstrings, or section banners. No extra scaffolding, no file I/O, and no class or helper unless the algorithm needs one (recursion, DFS, a search). Short names are fine (`n`, `s`, `a`, `ans`). Match the required output exactly.

Python 3:

- Read stdin with `input()`, in the shape the statement uses. Examples: `s = input()`, `n = int(input())`, `a = list(map(int, input().split()))`.
- Print with `print`.
- Put the logic at top level. No `if __name__ == "__main__"`.
- Use `sys.stdin.read()` only when the constraints make per-line `input()` too slow.

A locked language uses that same standard:

- Read stdin the usual way for that language and print the answer. C++ uses `cin` or `scanf` inside `int main()`. Java reads with `Scanner` or `BufferedReader`.
- Do not add a Python `if __name__ == "__main__"` guard.

The only goal is every test case passing.

## Workflow

When the user asks to submit or test a file they already wrote:
1. Check credentials exist (create if needed)
2. Confirm `contest_slug`, `question_slug`, and the code file path. Do not pass `--language`. The test and submit scripts choose it.
3. For testing: run `testCode.py` and show the result
4. For submitting: run `SubmitCode.py --wait` and show the submission result
5. If the user wants question slugs first, run `RetrieveAllChallenges.py`

When the user adds or names questions to solve, use the next section. Do not solve those questions in this chat, and do not ask which language to use.

## Solving questions in parallel

Use this when the user adds one or more questions, pastes contest URLs, or says to solve a contest or its unsolved questions.

Spawn one subagent per question, all in the same response, so the questions run at the same time. Contest time counts. The prompt below is the whole procedure.

### Step 1 — Which questions

If the user already gave slugs or URLs, use those. Slugs are the path segments described in How to find slugs.

If they asked to solve a contest and did not list questions:

```
cd <project_root> && python3 scripts/GetUnsolvedChallenges.py --contest <contest_slug>
```

Solve every object in the `unsolved` array. If the API has no solved field and every challenge comes back unsolved, solve them anyway and say that in the summary. Do not wait for confirmation.

### Step 2 — Spawn one agent per question

Launch every agent in parallel. One question, one agent, one file: `solutions/<question_slug>` plus the printed file extension.

If there are more than 10 questions, start the first 10 immediately. As soon as one finishes, start the next unsolved question. Do not pause between batches to ask.

Each agent receives this prompt:

```
You are solving one HackerRank challenge. Project root: <project_root>

Contest: <contest_slug>
Challenge: <question_slug> (<challenge_name>)

Do not search the web. Do not list directories. Do not grep. Do not read SKILL.md. Do not write a plan. Call 2 must be a real solution for the full problem, not a stub. Success is Accepted, every test passed.

1. cd <project_root> && python3 scripts/GetChallenge.py --contest <contest_slug> --question <question_slug>
2. Write <project_root>/solutions/<question_slug><file extension> on the next call. Obey Language lock, Use language, and File extension. No comments and no extra scaffolding. Python: input() and print, no main guard. Any other language: that language's normal stdin and stdout.
3. Run the samples when the platform has them:
   cd <project_root> && python3 scripts/testCode.py --contest <contest_slug> --question <question_slug> --file solutions/<question_slug><file extension> --timeout 20
   If the output says SOME FAILED, fix the file and run this again. Do not submit while any sample fails.
   If the output says ALL PASSED, submit.
   If it prints no test cases, there is nothing to gate on. Submit immediately.
4. Submit:
   cd <project_root> && python3 scripts/SubmitCode.py --contest <contest_slug> --question <question_slug> --file solutions/<question_slug><file extension> --wait --timeout 90

When there are no samples, the submit is still due within 2 minutes. If a judged test fails, edit that same file and submit again until Accepted. Report the challenge name, submission id, status, score, language, and how many test cases passed.
```

### Step 3 — Summarize results

After the agents finish, report:

| Challenge | Status | Score | Tests |
|-----------|--------|-------|-------|
| ...       | ...    | ...   | ...   |

Include any question that is still not Accepted, and the last status the judge returned.

## Watching for new questions

While a contest is open, poll it every 60 seconds:

```
python3 -u scripts/watch_new_challenges.py --contest <contest_slug> --interval 60
```

Run that under the monitor tool. The first pass records the challenges already listed and stays quiet. A later pass prints one `ACTION_REQUIRED` line only when a new slug appears. Spawn one solver per new slug in that same turn, using the prompt above. Do not ask the user. Leave the watcher running until it prints `DONE` because the contest ended.

## Updating Credentials

If the user gets 401/403 errors or wants to update their session:
```
python3 scripts/config.py --session "<new_session>" --csrf-token "<new_csrf_token>"
```
