#!/usr/bin/env python

import picamera
import argparse
from datetime import datetime
from time import sleep
import os


parser = argparse.ArgumentParser(
    description='Take photo and save it to the specified filename')

parser.add_argument("--filename", "-f",
                    help="specify the filename, where the pictures is saved. Default is the current timestamp")

parser.add_argument("--shutterspeed", "-ss", type=int,
                    help="set the shutterspeed to -ss ms")

parser.add_argument("--saturation", "-sa", type=int, default=0,
                    help="set image Saturation (-100 to 100)")

parser.add_argument("--sharpness", "-sh", type=int,
                    help="set image sharpness (-100 to 100)")

parser.add_argument("--iso", "-i", type=int, default=0,
                    help="set the ISO (0=auto,100,200,320,400,500,...)")

parser.add_argument("--hflip", action="store_true",
                    help="if set the image is flipped horizontally")

parser.add_argument("--vflip", action="store_true",
                    help="if set the image is flipped vertivally")

parser.add_argument("--rotation", "-r", type=int, default=0,
                    help="set roation. Allowed values are 0,90 , 180, 270")

parser.add_argument("--red", type=float,
                    help="set red gain for the AWB. If this AND --blue aren't set, automatic white balance will be used")

parser.add_argument("--blue", type=float,
                    help="set blue gain for the AWB")

parser.add_argument("--contrast", "-c", type=int, default=0,
                    help="set the contrast value. (-100 to 100)")

parser.add_argument("--brightness", "-b", type=int, default=50,
                    help="Set the brightness. (0 to 100)")

args = parser.parse_args()


cam = picamera.PiCamera()
cam.resolution = (2592, 1944)
cam.hflip = args.hflip
cam.vflip = args.vflip

if args.contrast:
    cam.contrast = args.contrast

if args.brightness:
    cam.brightness = args.brightness

if args.blue and args.red:
    cam.awb_mode = 'off'
    cam.awb_gains = (args.red, args.blue)

if args.shutterspeed:
    cam.shutter_speed = args.shutterspeed
    cam.exposure_mode = 'off'

if args.saturation:
    cam.saturation = args.saturation

if args.sharpness:
    cam.sharpness = args.sharpness

if args.filename:
    filename = args.filename

else:
    filename = "~/images/" + datetime.now().strftime("%Y-%m-%d_%X") + ".jpg"

cam.start_preview()
sleep(0.3)
cam.capture(filename)
# print(filename)
# print(cam.awb_gains)
# print(cam.exposure_speed)

if args.rotation == 90 or args.rotation == 270 or args.rotation == 180:
    cmd = "convert " + filename + " -rotate " + \
        str(args.rotation) + " " + filename
    os.system(cmd)
