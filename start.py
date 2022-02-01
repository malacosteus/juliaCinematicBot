#!/usr/bin/env python3.7

import subprocess
import time 
import os
import re
import signal
import logging

python_bin = "julia-movies-py37/bin/python3.7"
script = "bot.py"

def is_running(process):
    s = subprocess.Popen(["ps","axw"],stdout=subprocess.PIPE)
    for x in s.stdout:
        if re.search(process,x.decode("utf-8")):
                return True 
    return False



def main():
    try:
        subprocess.Popen([python_bin,script])
    finally:
        t_process = "python"
        if is_running(t_process):
            p = subprocess.Popen(['ps','-A'],stdout=subprocess.PIPE)
            out,err = p.communicate()
            for line in out.splitlines():
                if t_process in line.decode("utf-8"):
                    pid = int(line.split(None,1)[0])
                    print(os.kill(pid, signal.SIGTERM))

if __name__=='__main__':
    main()