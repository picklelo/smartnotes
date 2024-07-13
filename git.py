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

class GHIssue(rx.Base):
    number: int | None
    state: str | None
    title: str | None
    body: str | None
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    closed_at: datetime.datetime | None

def get_repo_stats():
    """Get stats for the repo."""
    stargazers = repo.stargazers_count
    watchers = repo.watchers_count
    forks = repo.forks_count
    subscribers = repo.subscribers_count
    open_issues = repo.open_issues_count
    return {
        "stargazers": stargazers,
        "watchers": watchers,
        "forks": forks,
        "subscribers": subscribers,
        "open_issues": open_issues,
    }

def get_github_issue(num: int):
    """Get the issue from the GitHub repository.
    
    Args:
        num: The issue number.
    """
    issue = repo.get_issue(num=num)
    return GHIssue(
        number=issue.number,
        state=issue.state,
        title=issue.title,
        body=issue.body,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        closed_at=issue.closed_at,
    )

def get_github_issues(sort: str = "state", state: str = "open", since: str | None = None,
    assignee: str | None = None,
) -> list[GHIssue]:
    """Get the issues from the GitHub repository.
    
    Args:
        sort (optional): The sort order of the issues.
        state (optional): The state of the issues.
        since (optional): The date to get issues since.
        assignee (optional): The assignee of the issues.
    """
    if since:   
        since = parser.parse(since)
    issues = repo.get_issues(sort=sort, state=state, since=since,
        assignee=assignee)
    print(dir(repo))
    issues = [
        GHIssue(
            number=issue.number,
            state=issue.state,
            title=issue.title,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            closed_at=issue.closed_at,
        )
        for issue in issues
    ]
    # with open("issues-open.txt", "w") as f:
    #     for issue in issues:
    #         print(issue.number)
    #         print(issue.number, issue.state, issue.title, issue.state)
    #         if issue.state == "open":
    #             f.write(f"{issue.number}, {issue.state}, {issue.title}, {issue.state}\n")
    return issues

# get_github_issues()
