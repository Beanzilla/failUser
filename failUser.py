#!/usr/bin/env python3
from json import loads, dumps
from json.decoder import JSONDecodeError
import pendulum
from subprocess import run, PIPE
from os.path import exists, join
from pyinotify import WatchManager, Notifier, ProcessEvent
from pyinotify import IN_MODIFY, IN_DELETE, IN_MOVE_SELF, IN_CREATE
import sys

# https://github.com/manos/python-inotify-tail_example/blob/master/tail-F_inotify.py

# Branch off the logging into a seperate file
from config import log, load_config, save_config, add_block, rm_block, check_blocks

myConfig = load_config()

myfile = myConfig["target"]
last_run = myConfig["last_unblock"]
bad_users = myConfig["bad_users"]

target = open(myfile, 'r')
target.seek(0,2)

WM = WatchManager()
dirmask = IN_MODIFY | IN_DELETE | IN_MOVE_SELF | IN_CREATE

def blocker(ip):
    # Utility function to block given ip as string
    #run(["iptables", "-I", "DOCKER-USER", "-i", "eth0", "-s", ip, "-j", "DROP"], stdout=PIPE, check=True)
    print("iptables -I DOCKER-USER -i eth0 -s {0} -j DROP".format(ip))

def unblocker(ip):
    # Utility function to unblock given ip as string
    #run(["iptables", "-D", "DOCKER-USER", "-i", "eth0", "-s", ip, "-j", "DROP"], stdout=PIPE, check=True)
    print("iptables -D DOCKER-USER -i eth0 -s {0} -j DROP".format(ip))

def is_bad(line):
    # Given line, attempt to parse... then is there a issue with it
    # Returns a python dict with ip and time in log
    if line: # Do we actually have something?
        try:
            j = loads(line)
            #if j["msg"] == "Attempt to login with banned username":
            if j["username"] in bad_users:
                r = {}
                r["ip"] = "{0}".format(j["ip"][7:])
                r["time"] = j["time"]
                return r
        except JSONDecodeError:
            log.error("Failed to decode line, '{0}'".format(line))

def checkup():
    # Check all our blocks
    unblocks = check_blocks()
    if unblocks:
        for ip in unblocks:
            log.info("Unblocked {0}".format(ip))
            unblocker(ip)
            rm_block(ip)

class EventHandler(ProcessEvent):
    def process_IN_MODIFY(self, event):
        if myfile not in join(event.path, event.name):
            return
        else:
            #luser = is_bad(target.readline().rstrip())
            for line in target.readlines():
                luser = is_bad(line.rstrip())
                if(luser):
                    blocker(luser["ip"])
                    now = pendulum.now().to_atom_string()
                    log.info("Blocked {0} at {1}".format(luser["ip"], now))
                    add_block(luser["ip"], now)


    def process_IN_MOVE_SELF(self, event):
        log.debug("Log file moved... continuing read on stale log!")

    def process_IN_CREATE(self, event):
        global target
        if myfile in join(event.path, event.name):
            target.close()
            target = open(myfile, 'r')
            log.debug("Log file created... Catching up!")
            for line in target.readlines():
                luser = is_bad(line.rstrip())
                if(luser):
                    blocker(luser["ip"])
                    now = pendulum.now().to_atom_string()
                    log.info("Blocked {0} at {1}".format(luser["ip"], now))
                    add_block(luser["ip"], now)
            target.seek(0,2)
        return

notifier = Notifier(WM, EventHandler())
index = myfile.rfind("/")
WM.add_watch(myfile[:index], dirmask)
last = pendulum.parse(last_run)

while True:
    try:
        now = pendulum.now()
        if now.diff(last).in_hours() > 1:
            last = now
            checkup()
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
    except KeyboardInterrupt:
        break

# Issue stop on event system
notifier.stop()
target.close()

# Update config
myConfig["last_unblock"] = last.to_atom_string()
save_config(myConfig)

exit(0)
