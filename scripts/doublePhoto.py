#!/usr/bin/env python

import os
from time import sleep
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='Take photo and save it to the specified filename')
parser.add_argument("--filename", "-f",
                    help="specify the filename, where the pictures is saved. Default is the current timestamp")


args = parser.parse_args()


filename = "~/images/"+datetime.now().strftime("%Y-%m-%d_%X")
if args.filename:
    filename = args.filename

#take the first photo on the local raspi
cmd = "/home/pi/bin/takePhoto.py -f " + filename + "right.jpg"
os.system(cmd)
print("first photo taken")

#take the second photo on the remote raspi and retrieve it
cmd = "sshpass -p \"raspberry\" ssh pi@raspi2 /home/pi/bin/takePhoto.py -f  " + filename + "left.jpg"
os.system(cmd)
#print(cmd)
print("second photo taken")
#sleep(0.5)
cmd = "sshpass -p \"raspberry\" scp pi@raspi2:" + filename +"left.jpg " + filename+"left.jpg"
os.system(cmd)
print("second photo retrieved")
