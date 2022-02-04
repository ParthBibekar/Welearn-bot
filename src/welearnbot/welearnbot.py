#!/usr/bin/env python3

from moodlews.service import MoodleClient

import welearnbot.action_handlers as handler
from welearnbot import resolvers
from welearnbot.constants import BASEURL, LINK_CACHE
from welearnbot.parser import setup_parser

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
        handler.handle_whoami(moodle)

    elif action == "courses":
        handler.handle_courses(moodle)

    elif action == "assignments":
        handler.handle_assignments(
            args, config, moodle, ignore_types, prefix_path, link_cache_filepath, token
        )

    elif action == "urls":
        handler.handle_urls(args, moodle)

    elif action == "files":
        handler.handle_files(
            args, moodle, ignore_types, prefix_path, link_cache_filepath, token
        )


if __name__ == "__main__":
    main()
