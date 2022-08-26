from argparse import Namespace
from configparser import RawConfigParser
import os
from time import time
from typing import List
from bs4 import BeautifulSoup as bs
from datetime import datetime

from moodlews.service import MoodleClient, ServerFunctions
from welearnbot import resolvers, utils
from welearnbot.constants import COURSE_CACHE
from welearnbot.gcal import publish_gcal_event


def handle_whoami(moodle: MoodleClient) -> None:
    info = moodle.server(ServerFunctions.SITE_INFO)
    print(info["fullname"])


def handle_courses(moodle: MoodleClient) -> None:
    # Get core user information
    info = moodle.server(ServerFunctions.SITE_INFO)
    userid = info["userid"]

    # Get enrolled courses information
    courses = moodle.server(ServerFunctions.USER_COURSES, {"userid": userid})
    for course in courses:
        course_name = course["fullname"]
        star = " "
        if course["isfavourite"]:
            star = "*"
        print(f" {star} {course_name}")


def handle_assignments(
    args: Namespace,
    config: RawConfigParser,
    moodle: MoodleClient,
    ignore_types: List[str],
    prefix_path: str,
    link_cache_filepath: str,
    token: str,
) -> None:
    link_cache = utils.read_cache(link_cache_filepath)
    # Get assignment data from server
    assignments = moodle.server(ServerFunctions.ASSIGNMENTS)

    file_statuses = []
    # Assignments are grouped by course
    for course in assignments["courses"]:
        course_name = course["shortname"]
        # Ignore unspecified courses
        if course_name not in args.courses:
            continue
        no_assignments = True
        for assignment in course["assignments"]:
            # Get the assignment name, details, due date, and relative due date
            assignment_id = assignment["id"]
            name = assignment["name"]
            duedate = datetime.fromtimestamp(int(assignment["duedate"]))
            due_str = duedate.strftime("%a %d %b, %Y, %H:%M:%S")
            duedelta = duedate - datetime.now()
            # Calculate whether the due date is in the future
            due = duedelta.total_seconds() > 0
            if args.dueassignments and not due:
                continue
            no_assignments = False
            if not no_assignments:
                print(course_name)
            # Show assignment details
            duedelta_str = (
                f"{abs(duedelta.days)} days, {duedelta.seconds // 3600} hours"
            )
            detail = bs(assignment["intro"], "html.parser").text
            print(f"    {name} - {detail}")
            for attachment in assignment["introattachments"]:
                print(f"        Attachment     : {attachment['filename']}")
                file_statuses.append(
                    utils.download_resource(
                        args,
                        moodle,
                        ignore_types,
                        attachment,
                        prefix_path,
                        course_name,
                        link_cache,
                        token,
                        indent=8,
                    )
                )
            if due:
                print(f"        Due on         : {due_str}")
                print(f"        Time remaining : {duedelta_str}")
            else:
                print(f"        Due on         : {due_str} ({duedelta_str} ago)")

            # Get submission details
            submission = moodle.server(
                ServerFunctions.ASSIGNMENT_STATUS, {"assignid": assignment_id}
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
                continue
            if not submission_made:
                print(f"        Submission     : NONE")

            # Write event to calendar
            if args.gcalendar and due:
                publish_gcal_event(
                    config, duedate, course_name, name, assignment_id, detail
                )
            print()

    utils.write_cache(link_cache_filepath, link_cache)
    utils.show_file_statuses(file_statuses, verbose=args.verbose)


def handle_submissions(
    args: Namespace,
    config: RawConfigParser,
    moodle: MoodleClient,
    ignore_types: List[str],
    prefix_path: str,
    link_cache_filepath: str,
    token: str,
) -> None:
    userid = resolvers.get_userid(moodle)

    submission_config = resolvers.resolve_submission_details(config)

    course_cache_filepath = os.path.join(prefix_path, COURSE_CACHE)
    courses_cache = utils.get_courses_cache(
        moodle, course_cache_filepath, userid, args.update_course_cache,
    )

    link_cache = utils.read_cache(link_cache_filepath)
    file_statuses = []
    for course in args.courses:
        if course not in courses_cache:
            print(f"{course} is not a valid course id")
            continue
        if args.rolls:
            rolls = utils.get_rolls(",".join(args.rolls))
        else:
            try:
                rolls = submission_config[course]
            except KeyError:
                print(
                    f'Could not resolve roll numbers for {course}. Please add it in your config or use "-r" flag'
                )
                continue
        if "ALL" in rolls:
            rolls = sorted(courses_cache[course]["participants"].keys())

        assignments = utils.fetch_assignments(moodle, courses_cache[course]["id"])
        for assignment in assignments:
            if assignment["duedate"] > time():
                continue
            for roll in rolls:
                submission_data = moodle.server(
                    ServerFunctions.SUBMISSION,
                    {
                        "assignid": assignment["id"],
                        "userid": courses_cache[course]["participants"][roll]["id"],
                    },
                )
                try:
                    file_data = submission_data["lastattempt"]["submission"]["plugins"][
                        0
                    ]["fileareas"][0]["files"]
                except KeyError:
                    continue
                if file_data:
                    file_statuses.append(
                        utils.download_resource(
                            args,
                            moodle,
                            ignore_types,
                            file_data[0],
                            prefix_path,
                            course,
                            link_cache,
                            token,
                            ["submissions", assignment["name"], roll],
                        )
                    )
    utils.write_cache(link_cache_filepath, link_cache)
    utils.show_file_statuses(file_statuses, verbose=args.verbose)


def handle_urls(args: Namespace, moodle: MoodleClient) -> None:
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


def handle_files(
    args: Namespace,
    config: RawConfigParser,
    moodle: MoodleClient,
    ignore_types: List[str],
    prefix_path: str,
    link_cache_filepath: str,
    token: str,
) -> None:
    link_cache = utils.read_cache(link_cache_filepath)
    course_ids = resolvers.get_courses_by_id(moodle, args)

    file_statuses = []

    # Iterate through each course, and fetch all modules
    for courseid in course_ids:
        course_name = course_ids[courseid]
        page = moodle.server(ServerFunctions.COURSE_CONTENTS, {"courseid": courseid})
        for item in page:
            modules = item.get("modules", [])
            for module in modules:
                modname = module.get("modname", "")
                if modname == "resource":
                    for resource in module["contents"]:
                        file_statuses.append(
                            utils.download_resource(
                                args,
                                moodle,
                                ignore_types,
                                resource,
                                prefix_path,
                                course_name,
                                link_cache,
                                token,
                            )
                        )
                elif modname == "folder":
                    folder_name = module.get("name", "")
                    for resource in module["contents"]:
                        file_statuses.append(
                            utils.download_resource(
                                args,
                                moodle,
                                ignore_types,
                                resource,
                                prefix_path,
                                course_name,
                                link_cache,
                                token,
                                subfolders=[folder_name],
                            )
                        )

    utils.write_cache(link_cache_filepath, link_cache)
    utils.show_file_statuses(file_statuses, verbose=args.verbose)
