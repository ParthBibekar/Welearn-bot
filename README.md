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

[files]
ignore = mp4,mkv
pathprefix = ~/welearn
```
You may omit any or all of your `[auth]` credentials, in which case you will be prompted each time you run the program.

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
Run `welearn_bot -h` to get the following help message.
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

# Google API

Follow the steps given below to create a Google Cloud Console and generate an OAuth2.0 Client ID (ClientSecret.json)

- Go to [Google cloud console](https://console.cloud.google.com/). If you are new to the platform you will see a prompt just click agree and continue.
- Click on "CREATE PROJECT" > Enter a suitable name leave the organization as "No Organization".
- In the search bar search for "google calendar api" and enable it.
- Click on Credentials > CONFIGURE CONSENT SCREEN
- Click External. Enter the "App Name", "User support email" and "Developer Contact Information". Click **SAVE AND CONTINUE**. Enter Test User's Email ID which you will be using to add events >  **SAVE AND CONTINUE** > **BACK TO DASHBOARD**.
- In API's & Services click on Credentials. **CREATE CREDENTIALS** > Set the Application type to "Desktop app" > Add the client name > **CREATE**.
- You will see a prompt just click OK and then in the OAuth 2.0 Client ID's click on the client name. You'll see a page with "Client ID" and "Client secret" values 
given on the right. Copy these and update your config file with the following lines, filling in your values.
```
[gcal]
client_id = xxxxxxxxxxxxxxx.apps.googleusercontent.com
client_secret = xxxxxxxxxxxxxxxxx
```

## Usage
```
py .\googleapi.py -d ALL
```
Just select the account of the test user or your own.

## Remember

The token expires after a day just delete the file and run the program again it will generate a new token.
