# Welearn-bot
This is a bot which lets you interact with WeLearn from the command line. It can
- Download all files/resources from your courses and organize them in designated folders.
- Show your assignments, filter due assignments.

Using the [Moodle Web Services API](https://docs.moodle.org/dev/Web_services) makes `welearn_bot.py` fast and robust.

### Demo
[![asciicast](https://asciinema.org/a/AgQTOCZlZmNW37oNeArZYnoBI.svg)](https://asciinema.org/a/AgQTOCZlZmNW37oNeArZYnoBI)

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
iusage: welearn_bot [-h] [-w] [-l] [-a] [-d] [-u] [-i [IGNORETYPES ...]] [-f] [-p PATHPREFIX] [courses ...]

A bot which can batch download files from WeLearn.

positional arguments:
  courses               IDs of the courses to download files from. The word ALL selects all configured courses.

optional arguments:
  -h, --help            show this help message and exit
  -w, --whoami          display logged in user name and exit
  -l, --listcourses     display configured courses (ALL) and exit
  -a, --assignments     show all assignments in given courses, download attachments and exit
  -d, --dueassignments  show only due assignments, if -a was selected
  -u, --urls            show all urls in given courses and exit
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
./welearn_bot.py --whoami
```
To get a list of courses specified in your configuration file, run
```
./welearn_bot.py -l
```
### Basic commands
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
To list all urls from the CH3303 course, run
```
./welearn_bot.py -u CH3303
```
### Ignoring filetypes
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
### Force downloads and pathprefix
To force download all resources from the course PH2202, even if already downloaded and present or set to be ignored, 
and put all the course directories in the `~/notes` folder, run
```
./welearn_bot.py -fp ~/notes PH2202
```


## TODO
- [x] Download files in separate directories
- [x] Allow multiple courses, list courses
- [x] Do not repeat downloads (cache past links)
- [x] List assignments
- [x] Deal with image files and other resources, which are nested within a resource page
- [x] Deal with files updated over time (check last modified)
- [ ] Allow finer control over resources to download (time range, filetype)

# Google API

Follow the steps given below to create a Google Cloud Console and generate an OAuth2.0 Client ID (ClientSecret.json)

- Go to console.cloud.google.com. If you are new to the platform you will see a prompt just click agree and continue.
- Click on "CREATE PROJECT" > Enter a suitable name leave the organization as "No Organization".
- In the search bar search for "google calendar api" and enable it.
- Click on Credentials > CONFIGURE CONSENT SCREEN
- Click External. Enter the "App Name", "User support email" and "Developer Contact Information". Click **SAVE AND CONTINUE**. Enter Test User's Email ID which you will be using to add events >  **SAVE AND CONTINUE** > **BACK TO DASHBOARD**.
- In API's & Services click on Credentials. **CREATE CREDENTIALS** > Set the Application type to "Desktop app" > Add the client name > **CREATE**.
- You will see a prompt just click OK and then in the OAuth 2.0 Client ID's click on the download Icon. Save the json file as "client_secret".

## Usage
```
py .\googleapi.py -d ALL
```
Just select the account of the test user or your own.

## Remember

The token expires after a day just delete the file and run the program again it will generate a new token.