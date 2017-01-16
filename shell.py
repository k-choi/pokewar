#!/home/kchoi/anaconda2/bin/python
# Shell Utility to test the Poke Work APIs
from __future__ import print_function
import sys
import subprocess as sp
import os

import poke_war_api as api

if __name__ == '__main__':
    cmd = sys.argv[1]
    if "who" == cmd:
        print("Retrieving who poked")
        l_names = api.find_who_poked()
        print(l_names)
    elif "add" == cmd:
        print("Starting fight with {}".format(sys.argv[2]))
        api.start_poke_war(sys.argv[2])
    elif "remove" == cmd:
        print("Ending fight with {}".format(sys.argv[2]))
        api.end_poke_war(sys.argv[2])
    elif "stat" == cmd:
        print("Retrieving stat for {}".format(sys.argv[2]))
        print(api.see_poke_stat(sys.argv[2]))
    elif "workstop" == cmd:
        print("Stopping the worker")
        api.stop_worker()
    elif "workstart" == cmd:
        print("Starting the worker")
        null_stream = open(os.devnull, 'w')
        sp.call("python worker.py &", shell=True, stdout=null_stream, stderr=sp.STDOUT)
    else:
        pass
