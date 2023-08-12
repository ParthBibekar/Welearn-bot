from moodlews.service import MoodleClient, ServerFunctions
from welearnbot.constants import ARCHIVE_TYPES

from argparse import Namespace
from typing import Any, Dict, List, Tuple

import json
import os
import mimetypes
import zipfile


def read_cache(filepath: str) -> dict:
    """Read from a cache file"""
    cache = dict()
    if os.path.exists(filepath):
        with open(filepath) as cache_file:
            cache = json.load(cache_file)
    return cache


def write_cache(filepath: str, cache: dict) -> None:
    """Update cache file"""
    with open(filepath, "w") as cache_file:
        json.dump(cache, cache_file)


def get_courses_cache(
    moodle: MoodleClient, course_cache_filepath: str, userid: str, update: bool = False,
):
    cache = read_cache(course_cache_filepath)
    if update or not cache:
        courses = moodle.server(ServerFunctions.USER_COURSES, {"userid": userid})
        for course in courses:
            courseid = course["shortname"]
            course_data = {
                "id": course["id"],
                "courseid": course["shortname"],
                "name": course["fullname"],
                "participants": {},
            }
            participants = moodle.server(
                ServerFunctions.COURSE_USERS, {"courseid": course["id"]}
            )
            for participant in participants:
                try:
                    print(participant["idnumber"])
                    course_data["participants"][participant["idnumber"]] = {
                        "id": participant["id"],
                        "name": participant["fullname"],
                    }
                except KeyError:
                    # skip caching details of participants whose information is not available.
                    # This mostly happens for instructors
                    continue
            cache[courseid] = course_data
    with open(course_cache_filepath, "w") as f:
        json.dump(cache, f)
    return cache


def fetch_assignments(moodle, courseid) -> List[Any]:
    assignments = moodle.server(
        ServerFunctions.ASSIGNMENTS, {"courseids[0]": courseid}  # cache[course]["id"]}
    )
    assignments = assignments["courses"][0]["assignments"]
    return [
        {
            "id": a["id"],
            "name": a["name"],
            "fileurl": a["introattachments"][0]["fileurl"]
            if a["introattachments"]
            else "",
            "duedate": a["duedate"],
            "opendate": a["allowsubmissionsfromdate"],
        }
        for a in assignments
    ]


def create_event(
    name: str, description: str, start: str, end: str, reminders: bool = True
) -> Dict[str, Any]:
    """Format and create a calendar event"""
    newevent = {
        "summary": name,
        "location": "",
        "description": description,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata",},
        "end": {"dateTime": end, "timeZone": "Asia/Kolkata",},
        "reminders": {
            "useDefault": reminders,
            "overrides": [{"method": "popup", "minutes": 10},],
        },
    }
    return newevent


def download_resource(
    args: Namespace,
    moodle: MoodleClient,
    ignore_types: List[str],
    resource: Any,
    prefix: str,
    course: str,
    cache: dict,
    token: str,
    subfolders: List[str] = [],
    indent: int = 0,
    extract: bool = True,
) -> Tuple[str, str]:
    """Helper function to retrieve a file/resource from the server"""
    filename = resource["filename"]
    subfolders = [subfolder.strip() for subfolder in subfolders]
    course_dir = os.path.join(prefix, course, *subfolders)
    fileurl = resource["fileurl"]
    _, extension = os.path.splitext(filename)
    extension = str.upper(extension[1:])
    if extension == "":
        # Missing extension - guess on the basis of the mimetype
        extension = mimetypes.guess_extension(resource["mimetype"])
        filename += extension
        extension = extension[1:]
    filepath = os.path.join(course_dir, filename)
    short_filepath = os.path.join(course, *subfolders, filename)
    timemodified = int(resource["timemodified"])

    # Only download if forced, or not already downloaded
    if not args.forcedownload and fileurl in cache:
        cache_time = int(cache[fileurl])
        # Check where the latest version of the file is in cache
        if timemodified == cache_time:
            if os.path.exists(filepath):
                return "EXISTS", short_filepath
            if not args.missingdownload and not os.path.exists(filepath):
                return "MISSING", short_filepath

    # Ignore files with specified extensions
    if extension in ignore_types:
        return "IGNORE", short_filepath

    # Create the course folder if not already existing
    if not os.path.exists(course_dir):
        os.makedirs(course_dir)

    # Download the file and write to the folder
    print(
        " " * indent + "Downloading " + short_filepath, end="", flush=True,
    )
    response = moodle.response(fileurl, token=token)
    with open(filepath, "wb") as download:
        download.write(response.content)

    # TODO: add option whether to extract or not in the config and flag
    if extension in ARCHIVE_TYPES and extract:
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(course_dir)
            print(" ... EXTRACTING", end="", flush=True)

    print(" ... DONE")

    # Add the file url to the cache
    cache[fileurl] = timemodified
    return "DOWNLOADED", short_filepath


def show_file_statuses(file_statuses, verbose=False) -> None:
    """Helper function to print ignored, missing files"""
    ignored = []
    missing = []
    downloaded = []
    for status, short_filepath in file_statuses:
        if status == "IGNORE":
            ignored.append(short_filepath)
        elif status == "MISSING":
            missing.append(short_filepath)
        elif status == "DOWNLOADED":
            downloaded.append(short_filepath)

    if len(ignored) > 0:
        if len(downloaded) > 0:
            print()
        if verbose:
            print("The following files have been ignored.")
            for short_filepath in ignored:
                print("    " + short_filepath)
        else:
            if len(ignored) == 1:
                print("1 file has been ignored, use --verbose for more info")
            else:
                print(
                    "{} files have been ignored, use --verbose for more info".format(
                        len(ignored)
                    )
                )

    if len(missing) > 0:
        if len(ignored) > 0 or len(downloaded) > 0:
            print()
        if verbose:
            print(
                "The following files are missing, use --missingdownload to download them."
            )
            for short_filepath in missing:
                print("    " + short_filepath)
        else:
            if len(missing) == 1:
                print("1 file is missing, use --verbose for more info")
            else:
                print(
                    "{} files are missing, use --verbose for more info".format(
                        len(missing)
                    )
                )


def get_rolls(roll_string: str) -> List[str]:
    roll_string = roll_string.strip().upper()
    if "ALL" in roll_string:
        return ["ALL"]
    raw_rolls = roll_string.split(",")
    rolls = []
    for i, roll in enumerate(raw_rolls):
        if roll == "...":
            rolls.extend(expand_dots(raw_rolls[i - 1], raw_rolls[i + 1]))
        else:
            rolls.append(roll)
    return rolls


def expand_dots(start: str, end: str):
    """
    Gives roll nos. between `start` and `end`
    """
    batch = start[:4]
    if batch != end[:4]:
        raise ValueError("Batch id before and after '...' does not match")
    start_roll = int(start[4:])
    end_roll = int(end[4:])
    return [f"{batch}{roll:03}" for roll in range(start_roll + 1, end_roll)]
