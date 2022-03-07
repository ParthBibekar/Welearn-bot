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
    urls        - lists urls\n\
    courses     - lists enrolled courses\n\
    whoami      - shows the user's name and exits\n\
    Abbreviations such as any one of 'f', 'a', 'u', 'c', 'w' are supported.",
    )
    parser.add_argument(
        "courses",
        nargs="*",
        help="IDs of the courses to download files from. The word ALL selects everything \nfrom the [courses] section in .welearnrc or welearn.ini",
    )
    parser.add_argument("--version", action="version", version="1.2.5")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show verbose warnings/errors",
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
        "-f",
        "--forcedownload",
        action="store_true",
        help="force download files even if already downloaded/ignored",
    )
    parser.add_argument(
        "-m",
        "--missingdownload",
        action="store_true",
        help="re-download those files which were downloaded earlier but deleted/moved from their location",
    )
    parser.add_argument(
        "-p",
        "--pathprefix",
        nargs=1,
        help="save the downloads to a custom path, overrides .welearnrc",
    )
    return parser
