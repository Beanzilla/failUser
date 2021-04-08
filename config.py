#!/usr/bin/env python3
from logging import basicConfig, DEBUG, INFO, WARN, ERROR, CRITICAL, getLogger
from logging.handlers import TimedRotatingFileHandler
from os.path import exists, join, dirname, abspath
from json import loads, dumps
from json.decoder import JSONDecodeError
import pendulum

# Get the full path for this file
currentdir = dirname(abspath(__file__))

# Target log file
TARGET = join("bbs", join("logs", "enigma-bbs.log"))

# Setup logging
# DEBUG, INFO, WARN, ERROR, CRITICAL
basicConfig(
    level=DEBUG,
    format="%(asctime)s - %(filename)s (%(lineno)d) - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        TimedRotatingFileHandler(
            filename=join(currentdir, "failUser.log"),
            when="midnight",
            backupCount=1,
        ),
        #logging.StreamHandler(stream=sys.stdout),
    ],
)

log = getLogger("failUser")

# Config JSON
def save_config(con):
    with open("failUser.cfg", "w") as f:
        f.write(dumps(con, indent=4, sort_keys=False))

def load_config():
    if not exists("failUser.cfg"):
        now = pendulum.now().to_datetime_string()
        defaults = {
            # Target enigma logs
            "target": "bbs/logs/enigma-bbs.log",
            # block_time in hours
            "block_time": 4,
            # Last unblock
            "last_unblock": now,
            # List of bad users to detect and block
            "bad_users": [
                "root",
                "postgres",
                "mysql",
                "apache",
                "nginx",
            ],
        }
        save_config(defaults)
        return defaults
    else:
        with open("failUser.cfg", "r") as f:
            config = loads(f.read())
        return config

# blocks in json
def add_block(ip, time):
    # first load in all blocks
    try:
        with open("blocks.json", "r") as f:
            blocks = loads(f.read())
    except FileNotFoundError:
        blocks = {}
        pass
    # add ip and time
    #log.debug("Added {0} in blocks.json".format(ip))
    blocks[ip] = time
    # update blocks
    with open("blocks.json", "w") as f:
        f.write(dumps(blocks))

def rm_block(ip):
    # first load all blocks
    try:
        with open("blocks.json", "r") as f:
            blocks = loads(f.read())
    except FileNotFoundError:
        return
    try:
        if blocks[ip]:
            #log.debug("Removed {0} in blocks.json".format(ip))
            del blocks[ip]
        # update blocks
        with open("blocks.json", "w") as f:
            f.write(dumps(blocks))
    except KeyError:
        log.debug("Unable to unblock '{0}'".format(ip))

def check_blocks():
    # return a list of ips exceeding block_time in config
    result = []
    conf = load_config()
    # load in blocks
    try:
        with open("blocks.json", "r") as f:
            blocks = loads(f.read())
    except FileNotFoundError:
        return
    now = pendulum.now()
    for ip in blocks:
        dt = pendulum.parse(blocks[ip])
        #log.debug("IP={0} TIME_LEFT={1}".format(ip, abs(now.diff(dt, False).in_hours())))
        if now.diff(dt).in_hours() > conf["block_time"]:
            # Oops, this ip needs to be unblocked
            result.append(ip)
    if result:
        return result