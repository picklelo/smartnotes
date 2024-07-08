import httpx
import os
import reflex as rx

class Project(rx.Base):
    id: str
    name: str

class State(rx.Base):
    name: str

class Issue(rx.Base):
    id: str
    title: str
    description: str | None
    state: State | None

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


def get_issues(project_name):
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
                                eq: "{project_name}"
                            }}
                        }}
                    }}
                ) {{ 
                    nodes {{ 
                        id 
                        title
                        description
                        state {{
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
                projects(after: $cursor, first: 50) {{ 
                    nodes {{ 
                        id 
                        name
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}""",
            "variables": {"cursor": cursor}  # Pass cursor as a variable
        }
        resp = make_request(data)
        print(resp)
        projects.extend([Project.parse_obj(project) for project in resp["data"]["projects"]["nodes"]])
        has_next_page = resp["data"]["projects"]["pageInfo"]["hasNextPage"]
        cursor = resp["data"]["projects"]["pageInfo"]["endCursor"]  # Update cursor for the next iteration
        if not has_next_page:
            break
    return projects

issues = get_issues("Radix")
print(len(issues))

# projects = get_all_projects()
# print(projects)
# print(len(projects))
# print("\n".join([p.id for p in projects]))
# resp = make_request(data)
# print(resp)
# print(len(resp))
