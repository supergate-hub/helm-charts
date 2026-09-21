"""Commit attribution profile: the right GitHub account.

A squash merge turns the authors of a pull request into `Co-authored-by` trailers on the commit
that lands on main, so a single commit made with a personal identity permanently credits the
wrong account in an organization repository. Authors must be an `@supergate.cc` address or the
noreply address of a `supergate-*` account; automation accounts are allowed.

No network or deployment credentials. Usage: check_commit_attribution.py [--head SHA]
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = (
    re.compile(r"[^@\s]+@supergate\.cc"),
    re.compile(r"\d+\+supergate-[A-Za-z0-9-]+@users\.noreply\.github\.com"),
    re.compile(r"(?:\d+\+)?(?:github-actions|dependabot|renovate)\[bot\]@users\.noreply\.github\.com"),
)


def allowed_author(email):
    return isinstance(email, str) and any(pattern.fullmatch(email) for pattern in ALLOWED)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).rstrip("\n")


def check_history(head):
    git("cat-file", "-e", head + "^{commit}")
    commits = git("rev-list", head).splitlines()
    errors = []
    for sha in commits:
        email = git("show", "-s", "--format=%ae", sha)
        if not allowed_author(email):
            errors.append(f"Commit {sha}: author <{email}> is not a supergate-hub identity; "
                          "commit as the organization account, not a personal address")
    return commits, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", help="commit to audit instead of the workflow event head")
    args = parser.parse_args()
    head = args.head
    if head is None:
        name = os.environ.get("GITHUB_EVENT_NAME")
        if name:
            event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
            if name == "pull_request":
                head = event["pull_request"]["head"]["sha"]
            elif name == "push":
                if event.get("deleted"):
                    print("Deleted ref: no commit to validate")
                    return 0
                head = event["after"]
            else:
                raise ValueError("unsupported event")
            if re.fullmatch(r"[a-f0-9]{40}", head) is None:
                raise ValueError("full commit SHA required")
        else:
            head = git("rev-parse", "HEAD")
    commits, errors = check_history(head)
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"Commit attribution passed: {len(commits)} commits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
