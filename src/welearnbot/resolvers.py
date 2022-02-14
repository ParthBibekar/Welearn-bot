from moodlews.service import MoodleClient, ServerFunctions
from welearnbot.utils import get_rolls

from argparse import Namespace
from configparser import RawConfigParser
from typing import Tuple, List

import errno
import getpass
import os
import sys


def resolve_action_mode(args: Namespace) -> str:
    # Get the mode
    action = ""
    if "files".startswith(args.action[0]):
        action = "files"
    elif "assignments".startswith(args.action[0]):
        action = "assignments"
    elif "submissions".startswith(args.action[0]):
        action = "submissions"
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
        print(
            "Can only use --dueassignments with 'assignments' action! Use the -h flag for usage."
        )
        sys.exit(errno.EPERM)
    if args.gcalendar and action != "assignments":
        print(
            "Can only use --gcalendar with 'assignments' action! Use the -h flag for usage."
        )
        sys.exit(errno.EPERM)
    if args.rolls and action != "submissions":
        print(
            "Can only use --rolls with 'submission' action! Use the -h flag for usage."
        )
        sys.exit(errno.EPERM)
    return action


def get_config() -> RawConfigParser:
    """Read the .welearnrc file from the home directory, and extract username and password"""
    if sys.platform == "linux" or sys.platform == "linux2":
        configfile = os.path.expanduser("~/.welearnrc")
    elif sys.platform == "darwin":
        configfile = os.path.expanduser("~/.welearnrc")
    elif sys.platform == "win32":
        configfile = os.path.expanduser("~/welearn.ini")

    config = RawConfigParser(allow_no_value=True)
    config.read(configfile)

    return config


def get_credentials(config: RawConfigParser) -> Tuple[str, str]:
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

    return username, password


def get_userid(moodle: MoodleClient):
    site_info = moodle.server(ServerFunctions.SITE_INFO)
    return site_info["userid"]


def get_all_courses(config: RawConfigParser) -> List[str]:
    """Also extract the list of `ALL` courses"""
    try:
        all_courses = list(config["courses"].keys())
    except KeyError:
        all_courses = []
    all_courses = map(str.strip, all_courses)
    all_courses = map(str.upper, all_courses)
    all_courses = list(all_courses)
    return all_courses


def resolve_submission_details(config: RawConfigParser,) -> dict[str, List[str]]:
    try:
        courses = dict(config["submissions"])
    except KeyError:
        print("Invalid configuration!")
        print("There is no field '[submissions]' in your config file")
        sys.exit(errno.ENODATA)

    submission_courses = {}
    for (key, val) in courses.items():
        submission_courses[key.upper()] = get_rolls(val)
    return submission_courses


def resolve_ignore_types(config: RawConfigParser, args: Namespace) -> List[str]:
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

    return ignore_types


def resolve_prefix_path(config: RawConfigParser, args: Namespace) -> str:
    # Read pathprefix from config
    try:
        prefix_path = os.path.expanduser(config["files"]["pathprefix"])
        prefix_path = os.path.abspath(prefix_path)
        if not os.path.isdir(prefix_path):
            print(
                prefix_path,
                "does not exist! Please create an empty directory ",
                prefix_path,
            )
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

    return prefix_path


def get_courses_by_id(moodle: MoodleClient, args: Namespace):
    # Get a list of all courses
    courses = moodle.server(ServerFunctions.ALL_COURSES)

    # Create a dictionary of course ids versus course names
    course_ids = dict()
    for course in courses["courses"]:
        course_name = course["shortname"]
        if course_name in args.courses:
            course_ids[course["id"]] = course_name
    return course_ids
