from moodlews.service import MoodleClient

from argparse import Namespace
from typing import Any, Dict, List

import json
import os
import mimetypes


def read_cache(filepath: str) -> dict:
    """Read from a cache file
    """
    cache = dict()
    if os.path.exists(filepath):
        with open(filepath) as cache_file:
            cache = json.load(cache_file)
    return cache


def write_cache(filepath: str, cache: dict) -> None:
    """Update cache file"""
    with open(filepath, "w") as cache_file:
        json.dump(cache, cache_file)


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


def get_resource(
    args: Namespace,
    moodle: MoodleClient,
    ignore_types: List[str],
    res: Any,
    prefix: str,
    course: str,
    cache: dict,
    token: str,
    subfolder: str = "",
    indent: int = 0,
) -> None:
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
    response = moodle.response(fileurl, token=token)
    with open(filepath, "wb") as download:
        download.write(response.content)
    print(" ... DONE")

    # Add the file url to the cache
    cache[fileurl] = timemodified

