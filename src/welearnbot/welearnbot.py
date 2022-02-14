#!/usr/bin/env python3

from moodlews.service import MoodleClient

import welearnbot.action_handlers as handler
from welearnbot import resolvers
from welearnbot.constants import BASEURL, COURSE_CACHE, LINK_CACHE
from welearnbot.parser import setup_parser
from welearnbot.utils import construct_course_cache, read_cache

import errno
import os
import sys


def main():
    # Get command line options
    parser = setup_parser()
    args = parser.parse_args()

    action = resolvers.resolve_action_mode(args)

    config = resolvers.get_config()
    username, password = resolvers.get_credentials(config)

    # Login to WeLearn with supplied credentials
    moodle = MoodleClient(BASEURL)
    token = moodle.authenticate(username, password)
    if not token:
        print("Invalid credentials!")
        sys.exit(errno.EACCES)

    userid = resolvers.get_userid(moodle)

    # Select all courses from config if `ALL` keyword is used
    if "ALL" in map(str.upper, args.courses):
        args.courses = resolvers.get_all_courses(config)

    ignore_types = resolvers.resolve_ignore_types(config, args)

    prefix_path = resolvers.resolve_prefix_path(config, args)

    submission_config = resolvers.resolve_submission_details(config)

    # Store cache file paths
    link_cache_filepath = os.path.join(prefix_path, LINK_CACHE)
    course_cache_filepath = os.path.join(prefix_path, COURSE_CACHE)
    course_cache = read_cache(course_cache_filepath)
    if not course_cache:
        course_cache = construct_course_cache(
            moodle, course_cache_filepath, userid, submission_config
        )

    # Action picker
    if action == "whoami":
        handler.handle_whoami(moodle)

    elif action == "courses":
        handler.handle_courses(moodle)

    elif action == "assignments":
        handler.handle_assignments(
            args, config, moodle, ignore_types, prefix_path, link_cache_filepath, token
        )

    elif action == "submissions":
        handler.handle_submissions(
            args,
            moodle,
            course_cache,
            submission_config,
            ignore_types,
            prefix_path,
            link_cache_filepath,
            token,
        )

    elif action == "urls":
        handler.handle_urls(args, moodle)

    elif action == "files":
        handler.handle_files(
            args, moodle, ignore_types, prefix_path, link_cache_filepath, token
        )


if __name__ == "__main__":
    main()
