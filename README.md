# Welearn-bot
This is a bot which lets you interact with WeLearn from the command line. It can
- Download all files/resources from your courses and organize them in designated folders.
- Show your assignments, filter due assignments.

Using the [Moodle Web Services API](https://docs.moodle.org/dev/Web_services) makes `welearn_bot.py` fast and robust.

### Demo
[![asciicast](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm.svg)](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm)

## Requirements
This script runs on `python3`. To install all dependencies (`requests` and `bs4`), run
```
pip3 install -r requirements.txt
```

## Configuration
On \*nix systems (linux, macos), create a `~/.welearnrc` file; on windows, create a `welearn.ini` in your `C:/Users/USERNAME/` folder.
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
ignore = mp4,mkv
pathprefix = ~/welearn
```
The `ALL` keyword will act as shorthand for the course names present in the `[courses]` section.
This way, you can choose to omit redundant courses in this section.

The `[files]` section lets you specify settings about the organization of your files.
All files with extensions listed in the `ignore` option will be not be downloaded.
This is useful for ignoring typically large files such as video files.
This setting is overridden by the `--ignoretypes` command line option, which in turn is overridden by the `--forcedownload` flag

The `pathprefix` is used to specify a common path for storing all your WeLearn course directories, which in turn store
your resources and assignment files.
This is overriden by the `--pathprefix` command line option.

## Usage
Run `./welearn_bot.py -h` to get the following help message.
```
usage: welearn_bot [-h] [-d] [-i [IGNORETYPES ...]] [-f] [-p PATHPREFIX] action [courses ...]

A command line client for interacting with WeLearn.

positional arguments:
  action                choose from
                            files       - downloads files/resources
                            assignments - lists assignments, downloads attachments
                            urls        - lists urls
                            courses     - lists enrolled courses
                            whoami      - shows the user's name and exits
                        Abbreviations such as any one of 'f', 'a', 'u', 'c', 'w' are supported.
  courses               IDs of the courses to download files from. The word ALL selects everything from the [courses] section in .welearnrc or welearn.ini

optional arguments:
  -h, --help            show this help message and exit
  -d, --dueassignments  show only due assignments with the 'assignments' action
  -i [IGNORETYPES ...], --ignoretypes [IGNORETYPES ...]
                        ignores the specified extensions when downloading, overrides .welearnrc
  -f, --forcedownload   force download files even if already downloaded/ignored
  -p PATHPREFIX, --pathprefix PATHPREFIX
                        save the downloads to a custom path, overrides .welearnrc
```

## Examples
### Testing your setup
If your `.welearnrc` or `welearn.ini` file is set up correctly, the following command should simply display your name.
```
./welearn_bot.py whoami
```
To get a list of courses you are enrolled in, run
```
./welearn_bot.py courses
```
### Basic commands
To pull all files from the courses MA1101 and CH3303, run
```
./welearn_bot.py files MA1101 CH3303
```
You can use the shorthand `f` for `files`, so the following is an equivalent command.
```
./welearn_bot.py f MA1101 CH3303
```
To show assignments and download their attachments from the course MA1101, run
```
./welearn_bot.py assignments MA1101
```
To list due assignments (due date in the future) from all courses, run
```
./welearn_bot.py -d assignments ALL
```
Make sure that the `-d` flag comes first!

To list all urls from the CH3303 course, run
```
./welearn_bot.py urls CH3303
```
### Ignoring filetypes
To download all resources from the course CH3303, ignoring pdf files, run
```
./welearn_bot.py -i pdf -- files CH3303
```
Note the use of `--` which is essential for separating the `IGNORETYPES` from the `courses`. The following format may be preferred.
```
./welearn_bot.py files CH3303 -i pdf
```
To override the `.welearnrc` ignore settings and allow all extensions, but still respect past downloads, run 
```
./welearn_bot.py -i -- files CH3303
```
### Force downloads and pathprefix
To force download all resources from the course PH2202, even if already downloaded and present or set to be ignored, 
and put all the course directories in the `~/notes` folder, run
```
./welearn_bot.py files PH2202 -fp ~/notes 
```


## TODO
- [x] Download files in separate directories
- [x] Allow multiple courses, list courses
- [x] Do not repeat downloads (cache past links)
- [x] List assignments
- [x] Deal with image files and other resources, which are nested within a resource page
- [x] Deal with files updated over time (check last modified)
- [ ] Allow finer control over resources to download (time range, filetype)
