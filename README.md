# Welearn-bot
This is a bot which lets you interact with WeLearn from the command line. It can
- Download all files/resources from your courses and organize them in designated folders.
- Show your assignments, filter due assignments.

### Demo
[![asciicast](https://asciinema.org/a/AgQTOCZlZmNW37oNeArZYnoBI.svg)](https://asciinema.org/a/AgQTOCZlZmNW37oNeArZYnoBI)

## Requirements
This script runs on `python3`. To install all dependencies (`requests` and `bs4`), run
```
pip3 install -r requirements.txt
```

## Configuration
On \*nix systems (linux, macos), create a `~/.welearnrc` file; on windows, create a `welearn.ini` in C:/Users/USERNAME/ Folder.
Inside, fill in your details in the following format.

```
[auth]
username = AzureDiamond
password = hunter2

[courses]
MA1101
PH2202
CH3303
LS4404
ES5505

[files]
ignore=mp4,mkv
```
The `ALL` keyword will act as shorthand for the course names present in the `[courses]` section.
This way, you can choose to omit redundant courses in this section.

The `[files]` section lets you specify settings about the organization of your files.
All files with extensions listed in the `ignore` option will be not be downloaded.
This is useful for ignoring typically large files such as video files.
This setting is overridden by the `--ignoretypes` flag, which in turn is overridden by the `--forcedownload` flag

## Usage
Run `./welearn_bot.py -h` to get the following help message.
```
usage: welearn_bot.py [-h] [-w] [-l] [-a] [-d] [-i [IGNORETYPES ...]] [-f] [courses ...]

A bot which can batch download files from WeLearn.

positional arguments:
  courses               IDs of the courses to download files from. The word ALL selects all configured courses.

optional arguments:
  -h, --help            show this help message and exit
  -w, --whoami          display logged in user name and exit
  -l, --listcourses     display configured courses (ALL) and exit
  -a, --assignments     show all assignments in given courses, download attachments and exit
  -d, --dueassignments  show only due assignments, if -a was selected
  -i [IGNORETYPES ...], --ignoretypes [IGNORETYPES ...]
                        ignores the specified extensions when downloading, overrides .welearnrc
  -f, --forcedownload   force download files even if already downloaded/ignored
```

### Examples
If your `.welearnrc` or `welearn.ini` file is set up correctly, the following command should simply display your name.
```
./welearn_bot.py --whoami
```
To pull all files from the courses MA1101 and CH3303, run
```
./welearn_bot.py MA1101 CH3303
```
To show all assignments and download their attachments from the course MA1101, run
```
./welearn_bot.py -a MA1101
```
To list due assignments (due date in the future) from all courses, run
```
./welearn_bot.py -ad ALL
```
To download all resources from the course CH3303, ignoring pdf files, run
```
./welearn_bot.py -i pdf -- CH3303
```
Note the use of `--` which is essential for separating the `IGNORETYPES` from the `courses`. The following format may be preferred.
```
./welearn_bot.py CH3303 -i pdf
```
To override the `.welearnrc` ignore settings and allow all extensions, but still respect past downloads, run 
```
./welearn_bot.py -i -- CH3303
```
To force download all resources from the course PH2202, even if already downloaded and present or set to be ignored, run
```
./welearn_bot.py -f PH2202
```
To get a list of courses specified in your `.welearnrc`, run
```
./welearn_bot.py -l
```

## TODO
- [x] Download files in separate directories
- [x] Allow multiple courses, list courses
- [x] Do not repeat downloads (cache past links)
- [x] List assignments
- [x] Deal with image files and other resources, which are nested within a resource page
- [ ] Allow finer control over resources to download (time range, filetype)
- [ ] Deal with files updated over time
