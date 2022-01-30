from typing import Any

import json
import os


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
) -> dict[str, Any]:
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

