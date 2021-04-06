# Welearn-bot
A bot that downloads all the necessary files from Welearn and moves them to designated folders on your local machine. It can also list all your assingnments with due dates.

## Dependencies
This script runs on python3, and requires the *requests* and *beautifulsoup4* libraries. Run `pip3 install requests bs4` to install them.

## Usage and configuration
Create a file in your home folder called `.welearnrc`. Inside, put your username in the first line and your password in the second line.

Run `./welearn_bot.py -h` to get the following help message.
```
usage: welearn_bot [-h] [-l] [-la] [-d] [courses ...]

A bot which can batch download files from WeLearn.

positional arguments:
  courses               IDs of the courses to download files from. The word ALL selects all available courses.

optional arguments:
  -h, --help            show this help message and exit
  -l, --listcourses     display available courses and exit
  -la, --listassignments
                        display available assignments in given courses and exit
  -d, --dueassignments  display only due assignments, if -la was selected
```

### Examples
To get a list of available courses, run
```
./welearn_bot.py -l
```
To pull all files from the courses AB1101 and XY5505, run 
```
./welearn_bot.py AB1101 XY5505
```
To list all assignments from the course AB1101, run
```
./welearn_bot.py -la AB1101
```
To list due assignments (due date in the future, no submission made) from all courses, run
```
./welearn_bot.py -la -d ALL
```

## TODO
- [x] Download files in separate directories
- [x] Allow multiple courses, list courses
- [x] Do not repeat downloads (cache past links)
- [x] List assignments
- [ ] Deal with image files, which are nested within html pages
- [ ] Allow finer control over resources to download (time range, filetype)
- [ ] Deal with files updated over time
