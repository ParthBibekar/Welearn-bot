#!/usr/bin/env python3

from moodlews.service import MoodleClient
from moodlews.service import ServerFunctions

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from bs4 import BeautifulSoup as bs
from configparser import RawConfigParser
from datetime import datetime
from datetime import timedelta
from sys import platform
import os, sys
import errno
import argparse
import json
import getpass
import mimetypes

# Read from a cache file
def read_cache(filepath):
    cache = dict()
    if os.path.exists(filepath):
        with open(filepath) as cache_file:
            cache = json.load(cache_file)
    return cache

# Update cache file
def write_cache(filepath, cache):
    with open(filepath, "w") as cache_file:
        json.dump(cache, cache_file)
    
# Format and create a calendar event
def create_event(name, description, start, end, reminders=True):
    newevent = {
        'summary': name,
        'location' : '',
        'description' : description,
        'start' : {
            'dateTime' : start,
            'timeZone' : 'Asia/Kolkata',
        },
        'end' : {
            'dateTime' : end,
            'timeZone' : 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': reminders,
            'overrides': [
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    return newevent


def main():
    # Server data
    baseurl = "https://welearn.iiserkol.ac.in"

    # Get command line options
    parser = argparse.ArgumentParser(description="A command line client for interacting with WeLearn.", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("action", nargs=1, help="choose from\n\
        files       - downloads files/resources\n\
        assignments - lists assignments, downloads attachments\n\
        urls        - lists urls\n\
        courses     - lists enrolled courses\n\
        whoami      - shows the user's name and exits\n\
    Abbreviations such as any one of 'f', 'a', 'u', 'c', 'w' are supported.")
    parser.add_argument("courses", nargs="*", help="IDs of the courses to download files from. The word ALL selects everything from the [courses] section in .welearnrc or welearn.ini")
    parser.add_argument("-d", "--dueassignments", action="store_true", help="show only due assignments with the 'assignments' action")
    parser.add_argument("-c", "--gcalendar", action="store_true", help="add due assignments to Google Calendar with the 'assignments' action")
    parser.add_argument("-i", "--ignoretypes", nargs="*", help="ignores the specified extensions when downloading, overrides .welearnrc")
    parser.add_argument("-f", "--forcedownload", action="store_true", help="force download files even if already downloaded/ignored")
    parser.add_argument("-p", "--pathprefix", nargs=1,  help="save the downloads to a custom path, overrides .welearnrc")

    args = parser.parse_args()

    # Get the mode
    action = ""
    if "files".startswith(args.action[0]):
        action = "files"
    elif "assignments".startswith(args.action[0]):
        action = "assignments"
    elif "urls".startswith(args.action[0]):
        action = "urls"
    elif "courses".startswith(args.action[0]):
        action = "courses"
    elif "whoami".startswith(args.action[0]):
        action = "whoami"
    else:
        print("Invalid action! Use the -h flag for usage.")
        sys.exit(errno.EPERM)

    if args.dueassignments and action != "assignments":
        print("Can only use --dueassignments with 'assignments' action! Use the -h flag for usage.")
        sys.exit(errno.EPERM)
    if args.gcalendar and action != "assignments":
        print("Can only use --gcalendar with 'assignments' action! Use the -h flag for usage.")
        sys.exit(errno.EPERM)

    # Read the .welearnrc file from the home directory, and extract username and password
    if platform == "linux" or platform == "linux2":
        configfile = os.path.expanduser("~/.welearnrc")
    elif platform == "darwin":
        configfile = os.path.expanduser("~/.welearnrc")
    elif platform == "win32":
        configfile = os.path.expanduser("~/welearn.ini")
    config = RawConfigParser(allow_no_value=True)
    config.read(configfile)

    username = ""
    password = ""
    try:
        username = config["auth"]["username"]
    except KeyError:
        username = input("Username : ")

    try:
        password = config["auth"]["password"]
    except KeyError:
        password = getpass.getpass("Password : ", stream=None)

    # Also extract the list of 'ALL' courses
    try:
        all_courses = list(config["courses"].keys())
    except KeyError:
        all_courses = []
    all_courses = map(str.strip, all_courses)
    all_courses = map(str.upper, all_courses)
    all_courses = list(all_courses)

    # Select all courses from config if 'ALL' keyword is used
    if 'ALL' in map(str.upper, args.courses):
        args.courses = all_courses

    # Read ignore types from config
    ignore_types = []
    try:
        ignores = config["files"]["ignore"]
        ignore_types = ignores.split(",")
    except KeyError:
        ignore_types = []

    # Override config with options
    if args.ignoretypes:
        ignore_types = args.ignoretypes

    # Override ignore with force
    if args.forcedownload:
        ignore_types = []

    ignore_types = map(str.strip, ignore_types)
    ignore_types = map(str.upper, ignore_types)
    ignore_types = list(ignore_types)

    # Read pathprefix from config
    try:
        prefix_path = os.path.expanduser(config["files"]["pathprefix"])
        prefix_path = os.path.abspath(prefix_path)
        if not os.path.isdir(prefix_path):
            print(prefix_path, "does not exist! Please create an empty directory ", prefix_path)
            sys.exit(errno.ENOTDIR)
    except KeyError:
        prefix_path = ""

    # Override pathprefix config if -p flag is used
    if args.pathprefix:
        prefix_path = os.path.expanduser(args.pathprefix[0])
        prefix_path = os.path.abspath(prefix_path)
        if not os.path.isdir(prefix_path):
            print(prefix_path, "does not exist!")
            sys.exit(errno.ENOTDIR)
    

    # Login to WeLearn with supplied credentials
    moodle = MoodleClient(baseurl)
    token = moodle.authenticate(username, password)
    if not token:
        print("Invalid credentials!")
        sys.exit(errno.EACCES)


    # Read google calendar info from config
    if args.gcalendar:
        try:
            OAUTH_CLIENT_ID = config["gcal"]["client_id"]
            OAUTH_CLIENT_SECRET = config["gcal"]["client_secret"]

            gcal_client_config = {
                "installed": {
                    "client_id": OAUTH_CLIENT_ID,
                    "client_secret": OAUTH_CLIENT_SECRET,
                    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token"
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
        SCOPES = ['https://www.googleapis.com/auth/calendar.events']
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
            with open(gcal_token_path, 'w') as gcal_token:
                gcal_token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)

    # Store cache file paths
    link_cache_filepath = os.path.join(prefix_path, ".link_cache")
    event_cache_filepath = os.path.expanduser("~/.welearn_event_cache")

    # Helper function to retrieve a file/resource from the server
    def get_resource(res, prefix, course, cache, subfolder="", indent=0):
        filename = res['filename']
        course_dir = os.path.join(prefix, course, subfolder)
        fileurl = res['fileurl']
        _, extension = os.path.splitext(filename)
        extension = str.upper(extension[1:])
        if extension == "":
            # Missing extension - guess on the basis of the mimetype
            extension = mimetypes.guess_extension(res["mimetype"])
            filename += extension
            extension = extension[1:]
        filepath = os.path.join(course_dir, filename)
        timemodified = int(res['timemodified'])

        # Only download if forced, or not already downloaded
        if not args.forcedownload and fileurl in cache:
            cache_time = int(cache[fileurl])
            # Check where the latest version of the file is in cache
            if timemodified == cache_time:
                return

        # Ignore files with specified extensions
        if extension in ignore_types:
            print(" " * indent + "Ignoring " + course, ":", filename)
            return

        # Create the course folder if not already existing
        if not os.path.exists(course_dir):
            os.makedirs(course_dir)

        # Download the file and write to the folder
        print(" " * indent + "Downloading " + os.path.join(course, subfolder, filename), end='')
        response = moodle.response(fileurl, token=token)
        with open(filepath, "wb") as download:
            download.write(response.content)
        print(" ... DONE")

        # Add the file url to the cache
        cache[fileurl] = timemodified

    def get_courses_by_id():
        # Get a list of all courses
        courses = moodle.server(ServerFunctions.ALL_COURSES)
            
        # Create a dictionary of course ids versus course names
        course_ids = dict()
        for course in courses['courses']:
            course_name = course['shortname']
            if course_name in args.courses:
                course_ids[course['id']] = course_name
        return course_ids

    
    # Action picker
    if action == "whoami":
        # Get core user information
        info = moodle.server(ServerFunctions.SITE_INFO)
        print(info['fullname'])
        sys.exit(0)

    elif action == "courses":
        # Get core user information
        info = moodle.server(ServerFunctions.SITE_INFO)
        userid = info["userid"]
        
        # Get enrolled courses information
        courses = moodle.server(ServerFunctions.USER_COURSES, userid=userid)
        for course in courses:
            course_name = course["fullname"]
            star = " "
            if course["isfavourite"]:
                star = "*"
            print(f" {star} {course_name}")
        sys.exit(0)

    elif action == "assignments":
        link_cache = read_cache(link_cache_filepath)
        if args.gcalendar:
            event_cache = read_cache(event_cache_filepath)
        # Get assignment data from server
        assignments = moodle.server(ServerFunctions.ASSIGNMENTS)

        # Assignments are grouped by course
        for course in assignments['courses']:
            course_name = course['shortname']
            # Ignore unspecified courses
            if course_name not in args.courses:
                continue
            no_assignments = True
            for assignment in course['assignments']:
                # Get the assignment name, details, due date, and relative due date
                assignment_id = assignment["id"]
                name = assignment['name']
                duedate = datetime.fromtimestamp(int(assignment['duedate']))
                due_str = duedate.strftime('%a %d %b, %Y, %H:%M:%S')
                duedelta = duedate - datetime.now()
                # Calculate whether the due date is in the future
                due = duedelta.total_seconds() > 0
                if args.dueassignments and not due:
                    continue
                no_assignments = False
                if not no_assignments:
                    print(course_name)
                # Show assignment details
                duedelta_str = f"{abs(duedelta.days)} days, {duedelta.seconds // 3600} hours"
                detail = bs(assignment['intro'], "html.parser").text
                print(f"    {name} - {detail}")
                for attachment in assignment['introattachments']:
                    print(f"        Attachment     : {attachment['filename']}")
                    get_resource(attachment, prefix_path, course_name, link_cache, indent=8)
                if due:
                    print(f"        Due on         : {due_str}")
                    print(f"        Time remaining : {duedelta_str}")
                else:
                    print(f"        Due on         : {due_str} ({duedelta_str} ago)")

                # Get submission details
                submission = moodle.server(ServerFunctions.ASSIGNMENT_STATUS, assignid=assignment_id)
                submission_made = False
                for plugin in submission['lastattempt']['submission']['plugins']:
                    if plugin['name'] == "File submissions":
                        for filearea in plugin['fileareas']:
                            if filearea['area'] == 'submission_files':
                                for submitted_file in filearea['files']:
                                    submission_made = True
                                    filename = submitted_file['filename']
                                    submission_date = datetime.fromtimestamp(int(submitted_file['timemodified']))
                                    submission_date_str = submission_date.strftime('%a %d %b, %Y, %H:%M:%S')
                                    print(f"        Submission     : {filename} ({submission_date_str})")
                if not submission_made:
                    print(f"        Submission     : NONE")

                # Write event to calendar
                if args.gcalendar and due:
                    # Put deadline at the *end* of the event
                    startdate = duedate - timedelta(hours = 1)
                    start_time = startdate.isoformat()
                    end_time = duedate.isoformat()
                    event_name = f"{course_name} - {name}"
                    if str(assignment_id) not in event_cache:
                        # Create and push a new event
                        event = create_event(event_name, detail, start_time, end_time, False)
                        added_event = service.events().insert(calendarId=gcal_calendar_id, body=event).execute()
                        event_id = added_event['id']
                        event_cache[assignment_id] = event_id
                        print(f"        Added event to calendar.")
                    else:
                        # Update event if necessary
                        event = service.events().get(calendarId=gcal_calendar_id, eventId=event_cache[str(assignment_id)]).execute()
                        if event['start']['dateTime'] != (start_time + "+05:30"):
                            event['start']['dateTime'] = start_time
                            event['end']['dateTime'] = end_time
                            updated_event = service.events().update(calendarId=gcal_calendar_id, eventId=event['id'], body=event).execute()
                            event_cache[assignment_id] = updated_event['id']
                            print(f"        Updated event in calendar.")
                print()

        write_cache(link_cache_filepath, link_cache)
        if args.gcalendar:
            write_cache(event_cache_filepath, event_cache)
        sys.exit(0)

    elif action == "urls":
        course_ids = get_courses_by_id()

        # Get a list of available urls
        urls = moodle.server(ServerFunctions.URLS)
        
        # Iterate through all urls, and build a dictionary
        url_list = dict()
        for url in urls['urls']:
            if url['course'] in course_ids:
                course_name = course_ids[url['course']]
                if not course_name in url_list:
                    url_list[course_name] = []
                url_list[course_name].append(url)

        # Display all urls
        for course_name in args.courses:
            if not course_name in url_list:
                continue
            no_url = True
            for url in url_list[course_name]:
                if no_url:
                    print(course_name)
                no_url = False
                url_name = url["name"]
                url_detail = bs(url["intro"], "html.parser").text
                url_link = url["externalurl"]
                print(f"    {url_name} - {url_detail}")
                print(f"        Link : {url_link}")
                print()
            print()
        sys.exit(0)

    elif action == "files":
        link_cache = read_cache(link_cache_filepath)
        course_ids = get_courses_by_id()

        # Iterate through each course, and fetch all modules
        for courseid in course_ids:
            course_name = course_ids[courseid]
            page = moodle.server(ServerFunctions.COURSE_CONTENTS, courseid=courseid)
            for item in page:
                modules = item.get("modules", [])
                for module in modules:
                    modname = module.get("modname", "")
                    if modname == "resource":
                        for resource in module["contents"]:
                            get_resource(resource, prefix_path, course_name, link_cache)
                    elif modname == "folder":
                        folder_name = module.get("name", "")
                        for resource in module["contents"]:
                            get_resource(resource, prefix_path, course_name, link_cache, subfolder=folder_name)

        
        write_cache(link_cache_filepath, link_cache)

if __name__ == '__main__':
    main()
