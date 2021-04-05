# Welearn-bot
A bot that downloads all the necessary files from all the course pages from Welearn and moves them to designated folders on your local machine.

## Usage and configuration
Create a file in your home folder called `.welearnrc`. Inside, put your username in the first line and your password in the second line.

Run `./welearn_bot.py -h` to get the following help message.
```
usage: welearn_bot.py [-h] [--listcourses] [courses ...]

WeLearn bot.

positional arguments:
  courses            IDs of the courses to download files from

optional arguments:
  -h, --help         show this help message and exit
  --listcourses, -l  display available courses and exit
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

## TODO
- [x] Download files in separate directories
- [x] Allow multiple courses, list courses
- [x] Do not repeat downloads (cache past links)
- [ ] Deal with image files, which are nested within html pages
- [ ] Allow finer control over resources to download (time range, filetype)
- [ ] Deal with files updated over time
