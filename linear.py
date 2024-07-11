from __future__ import annotations
import httpx
import os
import reflex as rx

class ProjectStatus(rx.Base):
    name: str

class State(rx.Base):
    name: str

class User(rx.Base):
    name: str

class Project(rx.Base):
    # id: str | None
    name: str
    status: ProjectStatus | None
    content: str | None
class Issue(rx.Base):
    identifier: str
    assignee: User | None
    title: str | None
    description: str | None
    state: State | None
    createdAt: str | None
    project: Project | None



# Assuming LINEAR_API_KEY is set in your environment variables
def make_request(data):
    linear_api_key = os.getenv("LINEAR_API_KEY")

    url = "https://api.linear.app/graphql"
    headers = {
        "Content-Type": "application/json",
        "Authorization": linear_api_key,
    }

    response = httpx.post(url, headers=headers, json=data)
    return response.json()


def get_issues(project_names):
    if isinstance(project_names, str):
        project_names = [project_names]
    cursor = None  # Initialize cursor
    issues = []
    while True:
        # Update the query to include a variable for the cursor
        data = {
            "query": f"""query GetIssues($cursor: String) {{
                issues(
                    first: 50,
                    after: $cursor,
                    filter: {{
                        project: {{
                            name: {{
                                in: {json.dumps(project_names)}
                            }}
                        }}
                        state: {{
                            name: {{
                                nin: ["Canceled"]
                            }}
                        }}
                    }}
                ) {{ 
                    nodes {{ 
                        identifier
                        title
                        description
                        state {{
                            name
                        }}
                        createdAt
                        assignee {{
                            name
                        }}
                        project {{
                            name
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}""",
            "variables": {"cursor": cursor},  # Pass cursor as a variable
        }
        print(data)
        resp = make_request(data)
        print(resp)
        issues.extend([Issue.parse_obj(issue) for issue in resp["data"]["issues"]["nodes"]])
        has_next_page = resp["data"]["issues"]["pageInfo"]["hasNextPage"]
        cursor = resp["data"]["issues"]["pageInfo"]["endCursor"]  # Update cursor for the next iteration
        if not has_next_page:
            break
    return issues

def get_all_projects():
    projects = []
    cursor = None  # Initialize cursor
    while True:
        # Update the query to include a variable for the cursor
        data = {
            "query": f"""query GetProjects($cursor: String) {{
                projects(
                    after: $cursor, 
                    first: 50,
                    filter: {{
                        status: {{
                            name: {{
                                nin: ["Canceled", "Completed", "Backlog"]
                            }}
                        }}
                        initiatives: {{
                            name: {{
                                eq: "Flexgen"
                            }}
                        }} 
                    }}
                ) {{ 
                    nodes {{ 
                        name
                        status {{
                            name
                        }}
                        content
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}""",
            "variables": {"cursor": cursor},  # Pass cursor as a variable
        }
        resp = make_request(data)
        print(resp)
        projects.extend([Project.parse_obj(project) for project in resp["data"]["projects"]["nodes"]])
        has_next_page = resp["data"]["projects"]["pageInfo"]["hasNextPage"]
        cursor = resp["data"]["projects"]["pageInfo"]["endCursor"]  # Update cursor for the next iteration
        if not has_next_page:
            break
    # Get issues for each project
    open_projects = [p for p in projects if p.status.name not in ["Canceled", "Completed", "Backlog", "Paused"]]
    open_projects.sort(key=lambda x: x.status.name)
    issues = get_issues([project.name for project in open_projects])
    for project in open_projects:
        if project.name in ["Open Source Bugs", "Templates and Recipes", "Core Graphing Improvements", "Reflex Web Performance"]:
            continue
        if project.status.name not in ["Paused"]:
            project.issues = [issue for issue in issues if issue.project.name == project.name]
        else:
            print("Skipping issues for paused project", project.name)
    return projects, open_projects

import json
# issues = get_issues("Flexgen V0")
# with open("context/linear-issues.json", "w") as f:
#     f.write(json.dumps([issue.dict() for issue in issues], indent=2))
# # print(json.dumps([issue.dict() for issue in issues], indent=2))

projects, open_projects = get_all_projects()
print(projects)
print(len(projects), len(open_projects))
# Sort by status
print(open_projects, len(open_projects))
with open("context/linear-projects.json", "w") as f:
    f.write(json.dumps([project.dict() for project in open_projects], indent=2))
# print("\n".join([p.name for p in projects]))
