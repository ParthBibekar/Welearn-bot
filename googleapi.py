from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from requests import Session
from bs4 import BeautifulSoup as bs
from configparser import RawConfigParser
from datetime import datetime
from datetime import timedelta
from sys import platform
import os, sys
import argparse
import json

# Get command line options
parser = argparse.ArgumentParser(description="A bot which can batch download files from WeLearn.")

parser.add_argument("courses", nargs="*", help="IDs of the courses to download files from. The word ALL selects all configured courses.")
parser.add_argument("-d", "--dueassignments", action="store_true", help="show only due assignments, if -a was selected")

args = parser.parse_args()
if len(args.courses) == 0 and not args.dueassignments:
    print("No course names selected. Use the -h flag for usage.")
    sys.exit()

if platform == "linux" or platform == "linux2":
    configfile = os.path.expanduser("~/.welearnrc")
elif platform == "darwin":
    configfile = os.path.expanduser("~/.welearnrc")
elif platform == "win32":
    configfile = os.path.expanduser("welearnrc.ini")

config = RawConfigParser(allow_no_value=True)
config.read(configfile)
username = config["auth"]["username"]
password = config["auth"]["password"]

all_courses = list(config["courses"].keys())
all_courses = map(str.strip, all_courses)
all_courses = map(str.upper, all_courses)
all_courses = list(all_courses)

# Select all courses from config if 'ALL' keyword is used
if 'ALL' in map(str.upper, args.courses):
    args.courses = all_courses

# Read from a cache of links
event_cache = set()
if os.path.exists(".event_cache"):
    with open(".event_cache") as event_cache_file:
        for event in event_cache_file.readlines():
            event_cache.add(event.strip())
print("Loaded event cache")


SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '../client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('calendar', 'v3', credentials=creds)
print("Loaded API service")


with Session() as s:
    # Login to WeLearn with supplied credentials
    login_url = "https://welearn.iiserkol.ac.in/login/token.php"
    login_response = s.post(login_url, data = {'username' : username, 'password' : password, 'service' : 'moodle_mobile_app'})
    token = json.loads(login_response.content)['token']

    server_url = "https://welearn.iiserkol.ac.in/webservice/rest/server.php"
    
    if args.dueassignments:
        # Get assignment data from server
        assignments_response = s.post(server_url, \
            data = {'wstoken' : token, 'moodlewsrestformat' : 'json', 'wsfunction' : 'mod_assign_get_assignments'})
        # Parse as json
        assignments = json.loads(assignments_response.content)

        # Assignments are grouped by course
        for course in assignments['courses']:
            course_name = course['shortname']
            # Ignore unspecified courses
            if course_name not in args.courses:
                continue
            no_assignments = True
            for assignment in course['assignments']:
                # Get the assignment name, details, due date, and relative due date
                name = assignment['name']
                assignment_id = assignment['id']
                duedate = datetime.fromtimestamp(int(assignment['duedate']))
                due_str = duedate.isoformat()
                duedelta = duedate - datetime.now()
                # Calculate whether the due date is in the future
                due = duedelta.total_seconds() > 0
                endtime = duedate + timedelta(hours = 1)
                end_str = endtime.isoformat()
                if assignment_id not in event_cache and due:
                    # Push the events to the calendar
                    newevent = {
                        'summary': assignment['name'],
                        'location' : '',
                        'description' : assignment['intro'],
                        'start' : {
                            'dateTime' : due_str,
                            'timeZone' : 'Asia/Kolkata',
                        },
                        'end' : {
                            'dateTime' : end_str,
                            'timeZone' : 'Asia/Kolkata',
                        },
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'popup', 'minutes': 10},
                            ],
                        },
                    }
                    print("Uploading Event : {} at time : {}".format(assignment['name'], due_str))
                    event_cache.add(assignment_id)
                    service.events().insert(calendarId='primary', body=newevent).execute()
    # Update cached event ids
    with open(".event_cache", "w") as event_cache_file:
        for event in list(event_cache):
            event_cache_file.write(str(event) + "\n")


