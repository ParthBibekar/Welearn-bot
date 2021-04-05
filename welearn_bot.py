#!/usr/bin/env python3

from requests import Session
from bs4 import BeautifulSoup as bs
import os, sys
import argparse
import urllib

# Get command line options
parser = argparse.ArgumentParser(description="A bot which can batch download files from WeLearn.")

parser.add_argument("courses", nargs="*", help="IDs of the courses to download files from")
parser.add_argument("-l", "--listcourses", action="store_true", help="display available courses and exit")

args = parser.parse_args()
if len(args.courses) == 0 and not args.listcourses:
    print("No course names selected. Use the -h flag for usage.")
    sys.exit()

# Read the .welearnrc file from the home directory, and extract username and password
configfile = os.path.expanduser("~/.welearnrc")
username = ''
password = ''
with open(configfile, "r") as config:
    lines = config.readlines()
    username = lines[0].strip()
    password = lines[1].strip()

with Session() as s:
    # Login to WeLearn with supplied credentials
    login_page = s.get("https://welearn.iiserkol.ac.in/login/")
    login_content = bs(login_page.content, "html.parser")
    token = login_content.find("input", {"name": "logintoken"})["value"]
    login_data = {"username": username,"password": password, "logintoken": token}
    s.post("https://welearn.iiserkol.ac.in/login/", login_data)
    home_page = s.get("https://welearn.iiserkol.ac.in/my/")
    home_content = bs(home_page.content, "html.parser")
    
    # Build a list of courses and course page links
    courses_list = home_content.find("li", {"data-key": "mycourses"})
    course_links = courses_list.findAll("a", "list-group-item")
    courses = dict()
    for course in course_links:
        course_url = course['href']
        course_name = course.find("span").contents[0]
        courses[course_name] = course_url
    
    # If specified, only display the list of courses and exit
    if args.listcourses:
        for name in courses.keys():
            print(name)
        sys.exit()
    
    # Read from a cache of links
    link_cache = set()
    if os.path.exists("link_cache"):
        with open("link_cache") as link_cache_file:
            for link in link_cache_file.readlines():
                link_cache.add(link.strip())
    
    # Loop through all given course IDs
    for selected_course_name in args.courses:
        # Ensure that the course name is valid
        if not selected_course_name in courses.keys():
            print(selected_course_name + " not in list of available courses!")
            continue

        # Get the course page and extract all links
        selected_course_page = s.get(courses[selected_course_name])
        selected_course_content = bs(selected_course_page.content, "html.parser")
        links = selected_course_content.findAll('a', "aalink")
        
        for link in links:
            # Skip cached links
            if link['href'] in link_cache:
                continue
            # Only download 'resource' links
            if ('/mod/resource/view.php' in link['href']):
                response = s.get(link['href'])
                # Extract the file name and put the file in an appropriate directory
                filename = urllib.parse.unquote(response.url.split("/")[-1])
                filepath = os.path.join(selected_course_name, filename)
                
                # Skip embedded resources. Temporary fix
                if filename.startswith("view.php"):
                    continue
                
                if not os.path.exists(selected_course_name):
                    os.makedirs(selected_course_name)
                
                with open(filepath, "wb") as download:
                    download.write(response.content)

                print("Downloaded " + filepath)
                link_cache.add(link['href'])

    # Update cached links
    with open("link_cache", "w") as link_cache_file:
        for link in list(link_cache):
            link_cache_file.write(link + "\n")
