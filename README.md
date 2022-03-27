# Welearn-bot
This is a bot which lets you interact with WeLearn from the command line. It can
- Download all files/resources from your courses and organize them in designated folders.
- Show your assignments, filter due assignments.
- Add your assignments to Google Calendar.


Go to our [project wiki](https://github.com/ParthBibekar/Welearn-bot/wiki) to learn more about configuring and using the script.
Developers may be interested in the article on [using the Moodle Web Service module](https://github.com/ParthBibekar/Welearn-bot/wiki/Using-the-Moodle-Web-Service-module),
which shows you how to use the accompanying `moodlews.service` module to write your own script for interacting with WeLearn, or indeed any other Moodle service.

### Demo
[![asciicast](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm.svg)](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm)

### Video Tutorial
We have a [Video Tutorial](https://youtu.be/hZfAOyDvK70) made in association with SlashDot Coding Club which goes over the Installation and Features of Welearn Bot on Windows and Linux.

[![Tutorial](http://img.youtube.com/vi/hZfAOyDvK70/0.jpg)](http://www.youtube.com/watch?v=hZfAOyDvK70 "SlashDot Tutorials: WelearnBot")

## Installation
This script runs on `python3`. To install it on your system, run
```
pip install --upgrade welearn-bot-iiserkol
```
The `--upgrade` flag ensures that you get the latest version.

If you are on Windows and are new to python, please go through this [quick guide](https://github.com/ParthBibekar/Welearn-bot/wiki/Installing-python-3.x-and-pip-on-Windows).

### Running from source
Clone this repo or download the source code, and navigate to that directory. To install dependencies, run
```
pip install -r requirements.txt
```
You can now navigate to the `src` directory and run `python welearn_bot [options ...]`.

## Configuration
On \*nix systems (linux, macos), create a `~/.welearnrc` file; on Windows, create a `welearn.ini` in your `C:/Users/USERNAME/` folder.
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
```

You may omit any or all of your `[auth]` credentials, in which case you will be prompted each time you run the program.

There are many more configuration options to explore, such as the `[files]` and `[gcal]` sections - for a detailed breakdown, please consult our
wiki page on [writing your configuration file](https://github.com/ParthBibekar/Welearn-bot/wiki/Writing-your-configuration-file).

### Google calendar integration
Integration with Google Calendar is completely optional. This feature allows you to save your assignment dates directly to Google Calendar, when you use the `--gcalendar` option.
You can also choose which calendar within your Google Calendar account to push events to.

You will have to authenticate using OAuth2.0 and add some lines to your configuration file.
Please follow the steps in the [Google Calendar integration](https://github.com/ParthBibekar/Welearn-bot/wiki/Google-Calendar-integration) article.
At the end, your configuration file will have a section of the following form.
```
[gcal]
client_id = xxxxxxxxxxxxxxx.apps.googleusercontent.com
client_secret = xxxxxxxxxxxxxxxxx
calendar_id = c_xxxxxxxxxxxxxxxxxxxxxxxxxx@group.calendar.google.com
```

## Usage
Run `welearn_bot -h` to get the following help message.
```
usage: welearn_bot [-h] [--version] [-v] [-d] [-c] [-i [IGNORETYPES ...]] [-f]
                   [-m] [-p PATHPREFIX]
                   action [courses ...]

A command line client for interacting with WeLearn.

positional arguments:
  action                choose from
                            files       - downloads files/resources
                            assignments - lists assignments, downloads attachments
                            urls        - lists urls
                            courses     - lists enrolled courses
                            whoami      - shows the user's name and exits
                            Abbreviations such as any one of 'f', 'a', 'u', 'c', 'w' are supported.
  courses               IDs of the courses to download files from. The word ALL selects everything
                        from the [courses] section in .welearnrc or welearn.ini

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         show verbose warnings/errors
  -d, --dueassignments  show only due assignments with the 'assignments' action
  -c, --gcalendar       add due assignments to Google Calendar with the 'assignments' action
  -i [IGNORETYPES ...], --ignoretypes [IGNORETYPES ...]
                        ignores the specified extensions when downloading, overrides .welearnrc
  -f, --forcedownload   force download files even if already downloaded/ignored
  -m, --missingdownload
                        re-download those files which were downloaded earlier but deleted/moved from their location
  -p PATHPREFIX, --pathprefix PATHPREFIX
                        save the downloads to a custom path, overrides .welearnrc
```
See our article on [using command line options](https://github.com/ParthBibekar/Welearn-bot/wiki/Using-command-line-options) for a detailed breakdown.

## Examples
### Testing your setup
If your `.welearnrc` or `welearn.ini` file is set up correctly, the following command should simply display your name.
```
welearn_bot whoami
```
To get a list of courses you are enrolled in, run
```
welearn_bot courses
```
### Basic commands
To pull all files from the courses MA1101 and CH3303, run
```
welearn_bot files MA1101 CH3303
```
You can use the shorthand `f` for `files`, so the following is an equivalent command.
```
welearn_bot f MA1101 CH3303
```
To show assignments and download their attachments from the course MA1101, run
```
welearn_bot assignments MA1101
```
To list due assignments (due date in the future) from all courses, run
```
welearn_bot -d assignments ALL
```
Make sure that the `-d` flag comes first!

To list all urls from the CH3303 course, run
```
welearn_bot urls CH3303
```
### Calendar integration
To list due assignments from all courses, and add them to your calendar, run
```
welearn_bot -dc assignments ALL
```
### Ignoring filetypes
To download all resources from the course CH3303, ignoring pdf files, run
```
welearn_bot -i pdf -- files CH3303
```
Note the use of `--` which is essential for separating the `IGNORETYPES` from the `courses`. The following format may be preferred.
```
welearn_bot files CH3303 -i pdf
```
To override the `.welearnrc` ignore settings and allow all extensions, but still respect past downloads, run 
```
welearn_bot -i -- files CH3303
```
### Force downloads and pathprefix
To force download all resources from the course PH2202, even if already downloaded and present or set to be ignored, 
and put all the course directories in the `~/notes` folder, run
```
welearn_bot files PH2202 -fp ~/notes 
```

### Missing downloads
If you've used `welearn_bot` to download some files, say from `MA1101`, but have subsequently deleted or moved them from the download location,
they will _not_ be downloaded again if you simply run
```
welearn_bot files MA1101
```
Instead, you will see a message calling these files `Missing`. To download these files again, run
```
welearn_bot -m files MA1101
```

