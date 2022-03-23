from argparse import ArgumentParser, RawTextHelpFormatter


def setup_parser() -> ArgumentParser:
    """Setups an argument parser"""
    parser = ArgumentParser(
        description="A command line client for interacting with WeLearn.",
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "action",
        nargs=1,
        help="choose from\n\
    files       - downloads files/resources\n\
    assignments - lists assignments, downloads attachments\n\
    submissions - lists submission count, downloads attachments\n\
    urls        - lists urls\n\
    courses     - lists enrolled courses\n\
    whoami      - shows the user's name and exits\n\
    Abbreviations such as any one of 'f', 'a', 's', 'u', 'c', 'w' are supported.",
    )
    parser.add_argument(
        "courses",
        nargs="*",
        help="IDs of the courses to download files from. The word ALL selects all courses \n\
    from [submissions] section in .welearnrc or welearn.ini for 'submissions' action\n\
    from the [courses] section in .welearnrc or welearn.ini for all other action",
    )
    parser.add_argument("--version", action="version", version="1.2.4")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show verbose warnings/errors",
    )
    parser.add_argument(
        "-d",
        "--dueassignments",
        action="store_true",
        help="show only due assignments with the 'assignments' action",
    )
    parser.add_argument(
        "-c",
        "--gcalendar",
        action="store_true",
        help="add due assignments to Google Calendar with the 'assignments' action",
    )
    parser.add_argument(
        "-i",
        "--ignoretypes",
        nargs="*",
        help="ignores the specified extensions when downloading, overrides .welearnrc",
    )
    parser.add_argument(
        "-r",
        "--rolls",
        nargs="*",
        help="roll numbers for which you want to download the submissions using the 'submissions' action",
    )
    parser.add_argument(
        "-p",
        "--pathprefix",
        nargs=1,
        help="save the downloads to a custom path, overrides .welearnrc",
    )
    parser.add_argument(
        "-f",
        "--forcedownload",
        action="store_true",
        help="force download files even if already downloaded/ignored",
    )
    parser.add_argument(
        "-u",
        "--update-course-cache",
        action="store_true",
        help="update course cache. Use this class when you change [submissions] section of config",
    )
    parser.add_argument(
        "-m",
        "--missingdownload",
        action="store_true",
        help="re-download those files which were downloaded earlier but deleted/moved from their location",
    )
    return parser
