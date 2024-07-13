from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials1.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service


def read_emails(max_results=10, query=None, label_ids=None):
    service = get_gmail_service()

    # Prepare the request parameters
    params = {"userId": "me", "maxResults": max_results}

    if query:
        params["q"] = query

    if label_ids:
        params["labelIds"] = label_ids
    else:
        params["labelIds"] = ["INBOX"]

    results = service.users().messages().list(**params).execute()
    messages = results.get("messages", [])

    if not messages:
        return []

    message_metadata = []
    for message in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=message["id"], format="metadata")
            .execute()
        )
        headers = {
            header["name"]: header["value"] for header in msg["payload"]["headers"]
        }

        metadata = {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "labelIds": msg["labelIds"],
            "snippet": msg["snippet"],
            "internalDate": msg["internalDate"],
            "subject": headers.get("Subject", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "date": headers.get("Date", ""),
        }

        message_metadata.append(metadata)

    return message_metadata
