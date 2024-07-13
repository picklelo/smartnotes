import os
import pickle
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_events(days_offset: int = 0, days_limit: int = 7):
    """Get events from Google Calendar for the number of days specified before and after today.

    Args:
        days_offset (int): The number of days after today to offset the start date. Default is 0.
        days_limit (int): The number of days after the start date to limit the events. Default is 7.

    Returns:
        list: A list of events with their details.
    """
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
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)

    # Get the current time
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    # Calculate the start date by subtracting 'days_offset' from the current time
    start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=days_offset))
    # Calculate the end date by adding 'days_limit' to the 'start_date'
    end_date = (start_date + datetime.timedelta(days=days_limit))
    # Convert 'start_date' and 'end_date' to ISO format strings
    start_date_iso = start_date.isoformat() + 'Z'
    end_date_iso = end_date.isoformat() + 'Z'

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary', timeMin=start_date_iso,
                                          timeMax=end_date_iso, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Format and return the events
    formatted_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        formatted_events.append({
            'summary': event['summary'],
            'start': start,
            'description': event.get('description', 'No description')
        })

    return formatted_events
