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
    site = s.get("https://welearn.iiserkol.ac.in/login/")
    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("input", {"name":"logintoken"})["value"]
    login_data = {"username": username,"password": password, "logintoken":token}
    s.post("https://welearn.iiserkol.ac.in/login/",login_data)
    home_page = s.get("https://welearn.iiserkol.ac.in/my/")
    # print(home_page.content)
    soup = bs(home_page.content, "html.parser")
    with open("output.html", "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify()))
        
    # We need to scrape objects with class="aalink coursename mr-2" 
    # URL from which pdfs to be downloaded
    coursesList = soup.find("li", {"data-key": "mycourses"})
    courseLinks = coursesList.findAll("a", "list-group-item")
    courses = dict()
    for course in courseLinks:
        courseUrl = course['href']
        courseName = course.find("span").contents[0]
        courses[courseName] = courseUrl
    
    if args.listcourses:
        for name in courses.keys():
            print(name)
        sys.exit()
    
    for selectedCourseName in args.courses:
        if not selectedCourseName in courses.keys():
            print(selectedCourseName + " not in list of available courses!")
            continue
        selectedCourse = s.get(courses[selectedCourseName])
        soup = bs(selectedCourse.content, "html.parser")
        with open(selectedCourseName + ".html", "w", encoding = 'utf-8') as file:
            # prettify the soup object and convert it into a string  
            file.write(str(soup.prettify()))
        
        links = soup.find_all('a',class_="aalink")
        # print(links)
        with open("links.html", "w", encoding = 'utf-8') as file:
            # prettify the soup object and convert it into a string
            for link in links:
                file.write(str(link.get('href')) + "\n")
                #print(link.get('href'))
        for link in links:
            if ('/mod/resource/view.php' in link.get('href')):
                
                response = s.get(link.get('href'))
                filename = urllib.parse.unquote(response.url.split("/")[-1])
                filepath = os.path.join(selectedCourseName, filename)
                
                if not os.path.exists(selectedCourseName):
                    os.makedirs(selectedCourseName)
                
                with open(filepath, "wb") as download:
                    download.write(response.content)

                print("File " + filepath + " downloaded")
