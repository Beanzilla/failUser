# failUser

This Python3 script allows you to block via IP tables bad user's who attempt to login to Enigma 1/2.

## Setup

1. Get the code, `git clone https://github.com/Beanzilla/failUser`
2. Initalize a Python Virtual Environment, `python3 -m venv env`
3. Activate Python venv `. env/bin/activate`
4. Installing what Python needs, `pip install -r require.txt`
5. Run `failUser.py` to create `failUser.cfg` (Then stop it)
6. Edit `failUser.cfg` with target Enigma 1/2 directory path, block_time in hours to block an IP.
7. Run it in the background `nohup ./failUser.py &` (Now you can close the connection yet still have failUser running)

(You can use the first step in Stopping it to tell if it's running)

## Configuration

The config `failuser.cfg` is in JSON, so just edit with your favorite text editor.

### target

This is the path to your enigma-bbs.log file. (It can be relative, but an exact is prefered)

Target the latests one not one that has .# at the very end.

### block_time

This is a whole number for how many hours to "block" the IP in the IP tables.

### last_unblock

Periodically the script will check a file it creates `blocks.json` to see if any blocked IPs need to be removed.

Please don't touch that, just let it be.

### bad_users

By default I include some common names users will wnat to try to login in as, use Enigma 1/2's configuration to flag usernames as invalid... this script will detect them and update it's config automatically.

See [here](https://nuskooler.github.io/enigma-bbs/configuration/config-hjson.html) for the Enigma 1/2's documentation on that. (Or the direct github reference within the default config [here](https://github.com/NuSkooler/enigma-bbs/blob/master/core/config_default.js#L52))

## Running after Setup

1. Activate Python venv, `. env/bin/activate`
2. Run it in the background `nohup ./failUser.py &` (Now you can close the connection yet still have failUser running)

(You can use the first step in Stopping it to tell if it's running) 

## Stopping it

1. Obtain it's Process ID (PID) via, `ps x | grep failUser`, (Your looking for the line with `python3` in it, that's failUser)
2. Issue `kill PID` Where PID is obtained from previous step (If all you see is `grep` in the line then failUser was not running)

## Debugging a crash

1. Look at `nohup.out` and or `failUser.log`
2. If needed make an issue here at this repo.
