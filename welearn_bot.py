#!/usr/bin/env python3

from requests import Session
from bs4 import BeautifulSoup as bs
import re
import shutil, os, sys
import argparse
import urllib

parser = argparse.ArgumentParser(description="WeLearn bot.")

parser.add_argument("courses", nargs="*", help="IDs of the courses to download files from")
parser.add_argument("--listcourses", "-l", action="store_true", help="display available courses and exit")

args = parser.parse_args()
if len(args.courses) == 0 and not args.listcourses:
    print("No course names selected. Use the -h flag for usage.")
    sys.exit()

# Create a file in your home directory called .welearnrc
# Put your username and password on separate lines
configfile = os.path.expanduser("~/.welearnrc")
username = ''
password = ''
with open(configfile, "r") as config:
    lines = config.readlines()
    username = lines[0].strip()
    password = lines[1].strip()

with Session() as s:
    login_page = s.get("https://welearn.iiserkol.ac.in/login/")
    login_content = bs(login_page.content, "html.parser")
    token = login_content.find("input", {"name": "logintoken"})["value"]
    login_data = {"username": username,"password": password, "logintoken": token}
    s.post("https://welearn.iiserkol.ac.in/login/", login_data)
    home_page = s.get("https://welearn.iiserkol.ac.in/my/")
    home_content = bs(home_page.content, "html.parser")
        
    courses_list = home_content.find("li", {"data-key": "mycourses"})
    course_links = courses_list.findAll("a", "list-group-item")
    courses = dict()
    for course in course_links:
        course_url = course['href']
        course_name = course.find("span").contents[0]
        courses[course_name] = course_url
    
    if args.listcourses:
        for name in courses.keys():
            print(name)
        sys.exit()
    
    for selected_course_name in args.courses:
        if not selected_course_name in courses.keys():
            print(selected_course_name + " not in list of available courses!")
            continue
        selected_course_page = s.get(courses[selected_course_name])
        selected_course_content = bs(selected_course_page.content, "html.parser")
        
        links = selected_course_content.findAll('a', "aalink")
        
        for link in links:
            if ('/mod/resource/view.php' in link.get('href')):
                
                response = s.get(link.get('href'))
                filename = urllib.parse.unquote(response.url.split("/")[-1])
                filepath = os.path.join(selected_course_name, filename)
                
                if not os.path.exists(selected_course_name):
                    os.makedirs(selected_course_name)
                
                with open(filepath, "wb") as download:
                    download.write(response.content)

                print("File " + filepath + " downloaded")
