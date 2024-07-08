from github import Github

# Authentication is defined via github.Auth
from github import Auth
import os
import reflex as rx


# using an access token
auth = Auth.Token(os.getenv("GITHUB_API_KEY"))

gh = Github(auth=auth)

repo = gh.get_repo("reflex-dev/reflex")

def get_issues():
    issues = repo.get_issues(sort="state", state="open")
    with open("issues-open.txt", "w") as f:
        for issue in issues:
            print(issue.number)
            print(issue.number, issue.state, issue.title, issue.state)
            if issue.state == "open":
                f.write(f"{issue.number}, {issue.state}, {issue.title}, {issue.state}\n")

get_issues()