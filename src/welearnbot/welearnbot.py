#!/usr/bin/env python3

from argparse import Namespace
from configparser import RawConfigParser
from moodlews.service import MoodleClient
from moodlews.service import ServerFunctions

from welearnbot.constants import BASEURL, LINK_CACHE
from welearnbot.gcal import publish_gcal_event
from welearnbot.parser import setup_parser
from welearnbot.utils import read_cache, write_cache
from welearnbot import resolvers

from typing import Any

from bs4 import BeautifulSoup as bs
from datetime import datetime
import os, sys
import errno
import mimetypes


def handle_whoami(moodle: MoodleClient) -> None:
    info = moodle.server(ServerFunctions.SITE_INFO)
    print(info["fullname"])
    sys.exit(0)


def handle_courses(moodle: MoodleClient) -> None:
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


def get_resource(
    args: Namespace,
    moodle: MoodleClient,
    ignore_types: list[str],
    res: Any,
    prefix: str,
    course: str,
    cache: dict,
    subfolder: str = "",
    indent: int = 0,
):
    """Helper function to retrieve a file/resource from the server"""
    filename = res["filename"]
    course_dir = os.path.join(prefix, course, subfolder)
    fileurl = res["fileurl"]
    _, extension = os.path.splitext(filename)
    extension = str.upper(extension[1:])
    if extension == "":
        # Missing extension - guess on the basis of the mimetype
        extension = mimetypes.guess_extension(res["mimetype"])
        filename += extension
        extension = extension[1:]
    filepath = os.path.join(course_dir, filename)
    short_filepath = os.path.join(course, subfolder, filename)
    timemodified = int(res["timemodified"])

    # Only download if forced, or not already downloaded
    if not args.forcedownload and fileurl in cache:
        cache_time = int(cache[fileurl])
        # Check where the latest version of the file is in cache
        if timemodified == cache_time:
            if os.path.exists(filepath):
                return
            if not args.missingdownload and not os.path.exists(filepath):
                print(" " * indent + "Missing     " + short_filepath)
                print(
                    " " * indent
                    + "    (previously downloaded but deleted/moved from download location, perhaps try --missingdownload)"
                )
                return

    # Ignore files with specified extensions
    if extension in ignore_types:
        print(" " * indent + "Ignoring    " + short_filepath)
        return

    # Create the course folder if not already existing
    if not os.path.exists(course_dir):
        os.makedirs(course_dir)

    # Download the file and write to the folder
    print(
        " " * indent + "Downloading " + short_filepath, end="", flush=True,
    )
    response = moodle.response(fileurl)
    with open(filepath, "wb") as download:
        download.write(response.content)
    print(" ... DONE")

    # Add the file url to the cache
    cache[fileurl] = timemodified


def handle_assignment(
    args: Namespace,
    config: RawConfigParser,
    moodle: MoodleClient,
    ignore_types: list[str],
    assignment: Any,
    course_name: str,
    prefix_path: str,
    link_cache: dict,
) -> None:
    # Get the assignment name, details, due date, and relative due date
    assignment_id = assignment["id"]
    name = assignment["name"]
    duedate = datetime.fromtimestamp(int(assignment["duedate"]))
    due_str = duedate.strftime("%a %d %b, %Y, %H:%M:%S")
    duedelta = duedate - datetime.now()
    # Calculate whether the due date is in the future
    due = duedelta.total_seconds() > 0
    if args.dueassignments and not due:
        return
    no_assignments = False
    if not no_assignments:
        print(course_name)
    # Show assignment details
    duedelta_str = f"{abs(duedelta.days)} days, {duedelta.seconds // 3600} hours"
    detail = bs(assignment["intro"], "html.parser").text
    print(f"    {name} - {detail}")
    for attachment in assignment["introattachments"]:
        print(f"        Attachment     : {attachment['filename']}")
        get_resource(
            args,
            moodle,
            ignore_types,
            attachment,
            prefix_path,
            course_name,
            link_cache,
            indent=8,
        )
    if due:
        print(f"        Due on         : {due_str}")
        print(f"        Time remaining : {duedelta_str}")
    else:
        print(f"        Due on         : {due_str} ({duedelta_str} ago)")

    # Get submission details
    submission = moodle.server(
        ServerFunctions.ASSIGNMENT_STATUS, assignid=assignment_id
    )
    submission_made = False
    try:
        for plugin in submission["lastattempt"]["submission"]["plugins"]:
            if plugin["name"] == "File submissions":
                for filearea in plugin["fileareas"]:
                    if filearea["area"] == "submission_files":
                        for submitted_file in filearea["files"]:
                            submission_made = True
                            filename = submitted_file["filename"]
                            submission_date = datetime.fromtimestamp(
                                int(submitted_file["timemodified"])
                            )
                            submission_date_str = submission_date.strftime(
                                "%a %d %b, %Y, %H:%M:%S"
                            )
                            print(
                                f"        Submission     : {filename} ({submission_date_str})"
                            )
    except KeyError:
        return
    if not submission_made:
        print(f"        Submission     : NONE")

    # Write event to calendar
    if args.gcalendar and due:
        publish_gcal_event(config, duedate, course_name, name, assignment_id, detail)
    print()


def main():
    # Get command line options
    parser = setup_parser()
    args = parser.parse_args()

    action = resolvers.resolve_action_mode(args)

    config = resolvers.get_config()
    username, password = resolvers.get_credentials(config)

    # Select all courses from config if `ALL` keyword is used
    if "ALL" in map(str.upper, args.courses):
        args.courses = resolvers.get_all_courses(config)

    ignore_types = resolvers.resolve_ignore_types(config, args)

    prefix_path = resolvers.resolve_prefix_path(config, args)
    # Login to WeLearn with supplied credentials
    moodle = MoodleClient(BASEURL)
    token = moodle.authenticate(username, password)
    if not token:
        print("Invalid credentials!")
        sys.exit(errno.EACCES)

    # Store cache file paths
    link_cache_filepath = os.path.join(prefix_path, LINK_CACHE)

    # Action picker
    if action == "whoami":
        handle_whoami(moodle)

    elif action == "courses":
        handle_courses(moodle)

    elif action == "assignments":
        link_cache = read_cache(link_cache_filepath)
        # Get assignment data from server
        assignments = moodle.server(ServerFunctions.ASSIGNMENTS)

        # Assignments are grouped by course
        for course in assignments["courses"]:
            course_name = course["shortname"]
            # Ignore unspecified courses
            if course_name not in args.courses:
                continue
            no_assignments = True
            for assignment in course["assignments"]:
                handle_assignment(
                    args,
                    config,
                    moodle,
                    ignore_types,
                    assignment,
                    course_name,
                    prefix_path,
                    link_cache,
                )

        write_cache(link_cache_filepath, link_cache)
        sys.exit(0)

    elif action == "urls":
        course_ids = resolvers.get_courses_by_id(moodle, args)

        # Get a list of available urls
        urls = moodle.server(ServerFunctions.URLS)

        # Iterate through all urls, and build a dictionary
        url_list = dict()
        for url in urls["urls"]:
            if url["course"] in course_ids:
                course_name = course_ids[url["course"]]
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
        course_ids = resolvers.get_courses_by_id(moodle, args)

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
                            get_resource(
                                args,
                                moodle,
                                ignore_types,
                                resource,
                                prefix_path,
                                course_name,
                                link_cache,
                            )
                    elif modname == "folder":
                        folder_name = module.get("name", "")
                        for resource in module["contents"]:
                            get_resource(
                                args,
                                moodle,
                                ignore_types,
                                resource,
                                prefix_path,
                                course_name,
                                link_cache,
                                subfolder=folder_name,
                            )

        write_cache(link_cache_filepath, link_cache)


if __name__ == "__main__":
    main()
