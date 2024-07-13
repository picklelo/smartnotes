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


class Milestone(rx.Base):
    name: str
    description: str | None
    targetDate: str | None
    issues: list[Issue] | None


# Assuming LINEAR_API_KEY is set in your environment variables
def make_request(data):
    linear_api_key = os.getenv("LINEAR_API_KEY")

    url = "https://api.linear.app/graphql"
    headers = {
        "Content-Type": "application/json",
        "Authorization": linear_api_key,
    }

    response = httpx.post(url, headers=headers, json=data)
    print(response.content)
    return response.json()


def paginated_query(query, name):
    cursor = None
    while True:
        data = {
            "query": query,
            "variables": {"cursor": cursor},
        }
        print("data")
        print(data)
        resp = make_request(data)
        print(resp)
        yield resp["data"][name]["nodes"]
        has_next_page = resp["data"][name]["pageInfo"]["hasNextPage"]
        cursor = resp["data"][name]["pageInfo"]["endCursor"]
        if not has_next_page:
            break


def get_milestones(project_name: str):
    """Get all the milestones for the given project.

    Args:
        project_name: The name of the project to get milestones for.
    """
    milestones = []
    query = f"""query GetMilestones($cursor: String) {{
        projectMilestones(
            after: $cursor, 
            first: 50,
            filter: {{
                project: {{
                    name: {{
                        eq: "{project_name}"
                    }}
                }}
            }}
        ) {{ 
            nodes {{ 
                name
                description
                targetDate
            }}
            pageInfo {{
                endCursor
                hasNextPage
            }}
        }}
    }}"""
    for resp in paginated_query(query, "milestones"):
        milestones.extend([Milestone.parse_obj(milestone) for milestone in resp])
    return milestones


def get_component_docs(component_name: str):
    """Get the documentation for the given component.

    Args:
        component_name: The name of the component to get documentation for.
    """
    # Get the response from github i.e. : https://raw.githubusercontent.com/reflex-dev/reflex-web/main/docs/library/forms/button.md
    import httpx

    response = httpx.get(
        f"https://raw.githubusercontent.com/reflex-dev/reflex-web/main/docs/library/forms/{component_name}.md"
    )
    return response.text


def get_issues(project_names: list[str]):
    """Get all the issues for the given projects.

    Args:
        project_names: The names of the projects to get issues for.
    """
    if isinstance(project_names, str):
        project_names = [project_names]
    issues = []
    # Update the query to include a variable for the cursor
    query = f"""query GetIssues($cursor: String) {{
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
    }}"""
    for resp in paginated_query(query, "issues"):
        print(resp)
        issues.extend([Issue.parse_obj(issue) for issue in resp])
    return issues


def get_active_projects():
    """Get all the active projects the team is currently working on."""


def get_project_info(project_name: str):
    """Get the info about a project and all its issues.

    Args:
        project_name: The name of the project to get info for.
    """
    projects = []
    query = f"""query GetProjects($cursor: String) {{
        projects(
            after: $cursor, 
            first: 50,
            filter: {{
                name: {{
                    eq: "{project_name}"
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
    }}"""
    for resp in paginated_query(query, "projects"):
        projects.extend([Project.parse_obj(project) for project in resp])
    if len(projects) == 0:
        return None
    project = projects[0]
    project.issues = get_issues._func(project.name)
    return project


def get_projects(initiative: str | None = None):
    """Get all the projects within the given initiative.

    Args:
        initiative: The initiative to filter by.
    """
    projects = []
    query = f"""query GetProjects($cursor: String) {{
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
                        eq: "{initiative}"
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
    }}"""
    for resp in paginated_query(query, "projects"):
        projects.extend([Project.parse_obj(project) for project in resp])

    # Get issues for each project
    open_projects = [
        p
        for p in projects
        if p.status.name not in ["Canceled", "Completed", "Backlog", "Paused"]
    ]
    # open_projects.sort(key=lambda x: x.status.name)
    # issues = get_issues._func([project.name for project in open_projects])
    # for project in open_projects:
    #     if project.name in ["Open Source Bugs", "Templates and Recipes", "Core Graphing Improvements", "Reflex Web Performance"]:
    #         continue
    #     if project.status.name not in ["Paused"]:
    #         project.issues = [issue for issue in issues if issue.project.name == project.name]
    #     else:
    #         print("Skipping issues for paused project", project.name)
    # return projects, open_projects
    return projects


import json

# print("getting issues")
# issues = get_issues._func("Flexgen V0")
# with open("context/linear-issues.json", "w") as f:
#     f.write(json.dumps([issue.dict() for issue in issues], indent=2))
# print(json.dumps([issue.dict() for issue in issues], indent=2))

# projects, open_projects = get_all_projects._func("Flexgen")
# projects = get_projects._func("Flexgen")
# open_projects = projects
# print(projects)
# print(len(projects), len(open_projects))
# # Sort by status
# print(open_projects, len(open_projects))
# with open("context/linear-projects.json", "w") as f:
#     f.write(json.dumps([project.dict() for project in open_projects], indent=2))
# print("\n".join([p.name for p in projects]))

# print(get_initiatives._func())
# print(get_milestones._func("Reverse Compiler"))
