from github import Github

# Authentication is defined via github.Auth
from github import Auth
import os
import reflex as rx

from smartnotes.ai.tool import tool
import datetime
from dateutil import parser


# using an access token
auth = Auth.Token(os.getenv("GITHUB_API_KEY"))

gh = Github(auth=auth)

repo = gh.get_repo("reflex-dev/reflex")

@tool
def get_github_issues(sort: str = "state", state: str = "open", since: datetime.datetime = None):
    if since:
        since = parser.parse(since)
    issues = repo.get_issues(sort=sort, state=state, since=since)
    with open("issues-open.txt", "w") as f:
        for issue in issues:
            print(issue.number)
            print(issue.number, issue.state, issue.title, issue.state)
            if issue.state == "open":
                f.write(f"{issue.number}, {issue.state}, {issue.title}, {issue.state}\n")
    return issues

# get_github_issues()
