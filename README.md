# Welearn-bot
This is a bot which lets you interact with WeLearn from the command line. It can
- Download all files/resources from your courses and organize them in designated folders.
- Show your assignments, filter due assignments.

Using the [Moodle Web Services API](https://docs.moodle.org/dev/Web_services) makes `welearn_bot` fast and robust.

### Demo
[![asciicast](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm.svg)](https://asciinema.org/a/LuVrCehQKXCBeCeXNRUZqgLdm)

## Installation
This script runs on `python3`. To install it on your system, run
```
pip install welearn-bot-iiserkol
```

### Running from source
Clone this repo or download the source code, and navigate to that directory. To install dependencies, run
```
pip install -r requirements.txt
```
You can now simply call the `welearn_bot` script using `python3`.

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

The `ALL` keyword will act as shorthand for the course names present in the `[courses]` section.
This way, you can choose to omit redundant courses in this section.


For more control over the organization of your files, add the `[files]` section to your config.
```
[files]
ignore = mp4,mkv
pathprefix = ~/welearn
```

All files with extensions listed in the `ignore` option will be not be downloaded.
This is useful for ignoring typically large files such as video files.
This setting is overridden by the `--ignoretypes` command line option, which in turn is overridden by the `--forcedownload` flag

The `pathprefix` is used to specify a common path for storing all your WeLearn course directories, which in turn store
your resources and assignment files.
This is overriden by the `--pathprefix` command line option.

### Google calendar integration
Integration with Google Calendar is completely optional. This feature allows you to save your assignment dates directly to Google Calendar, when you use the `--gcalendar` option.
You will have to authenticate using OAuth2.0 - follow the given step.

- Go to the [Google Cloud Console](https://console.cloud.google.com/), while logged in to your desired account. If you are new to the platform, you will be prompted to agree and continue.
- Click on _Create Project_. Enter a suitable name, and leave the organization blank.
- In the search bar, search for "Google Calendar API", and enable it.
- Click on _Credentials_ > _Configure Consent Screen_.
- Choose _External_. Enter the "App Name", "User support email" and "Developer Contact Information" with your desired values. Click _Save and Continue_.
- Fill in the "Test User's Email ID" with the address which you will be using to add events. Click _Save and Continue_ > _Back to Dashboard_.
- In "API's & Services", click on _Credentials_ > _Create Credentials_ > _OAuth client ID_. Set the Application type to "Desktop app", add a suitable client name, and click _Create_. Upon being prompted, click _OK_.
- In the "OAuth 2.0 Client ID's", click on the client name you just created. You'll see a page with "Client ID" and "Client secret" values 
given on the right. Copy these and add the following lines to your config file (`.welearnrc` or `welearn.ini`), filling in your values.
```
[gcal]
client_id = xxxxxxxxxxxxxxx.apps.googleusercontent.com
client_secret = xxxxxxxxxxxxxxxxx
```
When you run the program using the `--gcalendar` option for the first time, you will be taken to an OAuth2.0 login page in your browser.
You will stay logged in for at most a day.

If you want your events to be saved to a calendar other than your primary one, go to Google Calendar and create a new calendar.
Once it appears under "My Calendars", open its settings, scroll down to "Integrate calendar" and copy the "Calendar ID".
Update your config with this line under the `[gcal]` section.
```
calendar_id = c_xxxxxxxxxxxxxxxxxxxxxxxxxx@group.calendar.google.com
```

## Usage
Run `welearn_bot -h` to get the following help message.
```
usage: welearn_bot [-h] [-d] [-c] [-i [IGNORETYPES ...]] [-f] [-p PATHPREFIX] action [courses ...]

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
  -c, --gcalendar       add due assignments to Google Calendar with the 'assignments' action
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
