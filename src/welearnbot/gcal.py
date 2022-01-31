from welearnbot.constants import EVENT_CACHE

from typing import Any, Tuple

from configparser import RawConfigParser
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import errno
import os
import sys

from welearnbot.utils import create_event, read_cache, write_cache


def setup_gcal(config: RawConfigParser) -> Tuple[str, Any]:
    """Handle Google Calender

    Returns
    -------
    gcal_calendar_id: str
    service: Any
    """
    try:
        OAUTH_CLIENT_ID = config["gcal"]["client_id"]
        OAUTH_CLIENT_SECRET = config["gcal"]["client_secret"]

        gcal_client_config = {
            "installed": {
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
            }
        }
    except KeyError:
        print("Invalid configuration!")
        sys.exit(errno.ENODATA)

    try:
        gcal_calendar_id = config["gcal"]["calendar_id"]
    except KeyError:
        gcal_calendar_id = "primary"

    # Connect to the Google Calendar API
    SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
    creds = None
    gcal_token_path = os.path.expanduser("~/.gcal_token")
    if os.path.exists(gcal_token_path):
        creds = Credentials.from_authorized_user_file(gcal_token_path, SCOPES)
    # If there are no valid credentials, login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(gcal_client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(gcal_token_path, "w") as gcal_token:
            gcal_token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)

    return gcal_calendar_id, service


def publish_gcal_event(
    config: RawConfigParser,
    duedate: datetime,
    course_name: str,
    name: str,
    assignment_id: int,
    detail: str,
) -> None:
    event_cache_filepath = os.path.expanduser(EVENT_CACHE)
    event_cache = read_cache(event_cache_filepath)

    # Put deadline at the *end* of the event
    startdate = duedate - timedelta(hours=1)
    start_time = startdate.isoformat()
    end_time = duedate.isoformat()
    event_name = f"{course_name} - {name}"

    gcal_calendar_id, service = setup_gcal(config)

    assignment_id = str(assignment_id)
    if assignment_id not in event_cache:
        # Create and push a new event
        event = create_event(event_name, detail, start_time, end_time, False)
        added_event = (
            service.events().insert(calendarId=gcal_calendar_id, body=event).execute()
        )
        event_id = added_event["id"]
        event_cache[assignment_id] = event_id
        print(f"        Added event to calendar.")
    else:
        # Update event if necessary
        event = (
            service.events()
            .get(calendarId=gcal_calendar_id, eventId=event_cache[assignment_id],)
            .execute()
        )
        if event["start"]["dateTime"] != (start_time + "+05:30"):
            event["start"]["dateTime"] = start_time
            event["end"]["dateTime"] = end_time
            updated_event = (
                service.events()
                .update(calendarId=gcal_calendar_id, eventId=event["id"], body=event,)
                .execute()
            )
            event_cache[assignment_id] = updated_event["id"]
            print(f"        Updated event in calendar.")
    write_cache(event_cache_filepath, event_cache)

