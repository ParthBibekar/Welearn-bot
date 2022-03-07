from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
import json
import mimetypes
import os
from typing import Any, Dict, List, Tuple

from moodlews.service import MoodleClient


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


def create_event(
    name: str, description: str, start: str, end: str, reminders: bool = True
) -> Dict[str, Any]:
    """Format and create a calendar event"""
    newevent = {
        "summary": name,
        "location": "",
        "description": description,
        "start": {
            "dateTime": start,
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end,
            "timeZone": "Asia/Kolkata",
        },
        "reminders": {
            "useDefault": reminders,
            "overrides": [
                {"method": "popup", "minutes": 10},
            ],
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
) -> Tuple[str, str]:
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
        " " * indent + "Downloading " + short_filepath,
        flush=True,
    )
    response = moodle.response(fileurl, token=token)
    with open(filepath, "wb") as download:
        download.write(response.content)
    print(" " * indent + short_filepath + " ... DONE", flush=True)

    # Add the file url to the cache
    cache[fileurl] = timemodified
    return "DOWNLOADED", short_filepath


def get_resources(
    args: Namespace,
    moodle: MoodleClient,
    ignore_types: List[str],
    resources_data: List[Tuple[Any, str]],
    prefix: str,
    course: str,
    cache: dict,
    token: str,
) -> List[Tuple[str, str]]:
    """
    This is a wrapper over get_resource that parallelizes downloads

    resources_data_list is a list of resource_data
    where resource_data is the data of what needs to be downloaded with
    it's folder location like this
    Tuple[resource, subfolder]
    """

    def _get_resource(resource_data: Tuple[Any, str]) -> Tuple[str, str]:
        resource, folder_name = resource_data
        return get_resource(args,
                            moodle,
                            ignore_types,
                            resource,
                            prefix,
                            course,
                            cache,
                            token,
                            subfolder=folder_name)

    with ThreadPoolExecutor() as exe:
        file_statuses = exe.map(_get_resource, resources_data)

    # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.map
    # exception hanlding must be done while retrieving
    # the items for the map's iterator
    # ie, exceptions will be raised here while converting iterator in to list
    return list(file_statuses)


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
