#!/usr/bin/env python

import argparse
import csv
import numpy as np
import cv2
import sys

parser = argparse.ArgumentParser(description='calibrate the stereo cameras with images of checkerboards')
parser.add_argument("--images" ,"-i", default="../data/stereo_pairs.csv",
                    help="a csv-list with the image pairs to be used for calibration. Each line should contain two filenames, first the right image, then the left image")

parser.add_argument("--outfile", "-o", default="stereoParams",
                    help="where the calculated undistortion parameters should be stored")

parser.add_argument("--width", "-w", default=8,
                    help="widht of the checkerboard")

parser.add_argument("--height", "-he", default=6,
                    help="height of the checkerboard")

args = parser.parse_args()

with open(args.images, 'r') as f:
    reader = csv.reader(f)
    images = list(reader)

if (len(images)<7):
    print("not enough images supplied. Exiting")
    sys.exit()

#termination criteria
criteria = (cv2.TERM_CRITERIA_EPS  + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((args.height*args.width,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpointsR = [] # 2d points in image plane.
imgpointsL = []

for i in range(len(images)):
    imgR = cv2.imread(images[i][0])
    imgL = cv2.imread(images[i][1])
    
    grayR = cv2.cvtColor(imgR,cv2.COLOR_BGR2GRAY)
    grayL = cv2.cvtColor(imgL,cv2.COLOR_BGR2GRAY)
    print("read and converted", images[i])

    # Find the chess board corners
    retR, cornersR = cv2.findChessboardCorners(grayR, (args.width,args.height),None)
    retL, cornersL = cv2.findChessboardCorners(grayL, (args.width,args.height),None)
    print("found corners")

    # If found, add object points, image points (after refining them)
    if retR == True and retL == True:
        objpoints.append(objp)

        corners2R = cv2.cornerSubPix(grayR,cornersR,(11,11),(-1,-1),criteria)
        imgpointsR.append(corners2R)
        corners2L = cv2.cornerSubPix(grayL,cornersL,(11,11),(-1,-1),criteria)
        imgpointsL.append(corners2L)
        print(i)
        # Draw and display the corners
        imgR = cv2.drawChessboardCorners(imgR, (args.width,args.height), corners2R,retR)
        cv2.startWindowThread()
        cv2.namedWindow('imgR', cv2.WINDOW_NORMAL)
        cv2.imshow('imgR',imgR)
        imgL = cv2.drawChessboardCorners(imgL, (args.width,args.height), corners2L,retL)
        cv2.startWindowThread()
        cv2.namedWindow('imgL', cv2.WINDOW_NORMAL)
        cv2.imshow('imgL',imgR)

cv2.destroyAllWindows()

if (len(objpoints) < 7):
    print("not enough pairs found. Exiting")
    sys.exit()

#calculate the intrinsic parameters
retR, CMR , DCR, rvecsR, tvecsR = cv2.calibrateCamera(objpoints,imgpointsR,grayR.shape[::-1], None, None)
retL, CML , DCL, rvecsL, tvecsL = cv2.calibrateCamera(objpoints,imgpointsL,grayL.shape[::-1], None, None)

R = np.zeros([3,3])
T = np.zeros([3])
E = np.zeros([3,3])

#stereocalib_flags = cv2.CALIB_FIX_INTRINSIC | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_FIX_FOCAL_LENGTH | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_FIX_K3 | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5
stereocalib_flags = cv2.CALIB_FIX_INTRINSIC | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_FIX_FOCAL_LENGTH
stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
retval, CMR, DCR, CML, DCL, R, T, E, F =  cv2.stereoCalibrate(objpoints,imgpointsR,imgpointsL, criteria=stereocalib_criteria, flags=stereocalib_flags,
                                                              imageSize=grayR.shape[::-1], cameraMatrix1=CMR, cameraMatrix2=CML, distCoeffs1=DCR,
                                                              distCoeffs2=DCL)

RR = np.zeros([3,3])
RL = np.zeros([3,3])
PR = np.zeros([3,4])
PL = np.zeros([3,4])
Q = np.zeros([4,4])

#calculate the extrinsic parameters and save them
RR,RL,PR,PL,Q,ROIR,ROIL = cv2.stereoRectify(CMR,DCR,CML,DCL,grayL.shape[::-1],R,T)
np.savez(args.outfile,CMR=CMR,CML=CML,DCR=DCR,DCL=DCL,R=R,T=T,E=E,F=F,PR=PR,PL=PL,RR=RR,RL=RL,Q=Q,ROIR=ROIR,ROIL=ROIL)
