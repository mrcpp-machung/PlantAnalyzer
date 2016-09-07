import cv2
import numpy as np
from config import config


def alignImages(im1, im2, showMatches=False, threshold=0.5,
                resizefactor=0.5, append_text_to_statusbar=None):
    """
    expects two images, assumes that both of them are grayscale of both them are RGB.
    Returns an aligned version of im2 in the size of im1
    Parameters:
        -im1: Any opencv image
        -im2: OpenCV image with the same color space
        -showMatches: If 1, the matches are shown. Default = 0
        -threshold: Parameter, how good the matches must be to be considered. Default = 0.5
                    If too low, not enough matches might be found. If too high the alignment may fail
        -resizefactor: The factor, by which the images are resized
         for the sift-detector. Too high -> too much RAM usage. Too low -> not accurate enough
    """
    # Resize images for less ram usage
    im1small = cv2.resize(im1, None, fx=resizefactor,
                          fy=resizefactor, interpolation=cv2.INTER_AREA)
    im2small = cv2.resize(im2, None, fx=resizefactor,
                          fy=resizefactor, interpolation=cv2.INTER_AREA)

    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()
    print("sift initialisiert")
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(im1small, None)
    kp2, des2 = sift.detectAndCompute(im2small, None)
    print("keypoints found")

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    print("matches found")

    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < threshold * n.distance:
            good.append(m)

    MIN_MATCH_COUNT = 10

    if (showMatches is True):
        result = cv2.drawMatches(
            im1small, kp1, im2small, kp2, good, flags=2, outImg=None)
        cv2.startWindowThread()
        cv2.namedWindow("Matches", cv2.WINDOW_NORMAL)
        cv2.imshow("Matches", result)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32(
            [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32(
            [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
#        matchesMask = mask.ravel().tolist()

#        h = im2.shape[0]
#        w = im2.shape[1]
#        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1],
#                          [w - 1, 0]]).reshape(-1, 1, 2)
#        dst = cv2.perspectiveTransform(pts, M)

        result = cv2.warpPerspective(
            im2, M, (im1.shape[1], im1.shape[0]), flags=cv2.WARP_INVERSE_MAP)

    else:
        print("Not enough matches are found - %d/%d" %
              (len(good), MIN_MATCH_COUNT))
#        matchesMask = None

    return result


def cropFrame(im, framesize=0.1):
    """
    Parameters:
        - im: is the image to be cropped
        - framesize: is the relative size of the frame, that needs to be cropped away. e.g. 0.1 equals a frame
                    10% of the size of image
    """
    width = len(im[0:])
    height = len(im[0, 0:])
    cropwidth = int(width * framesize)
    cropheight = int(height * framesize)
    result = np.copy(im[cropwidth:width - cropwidth,
                        cropheight:height - cropheight])
    return result


def floatIm2RGB(floatIm):
    """
    converts a float Image to a normalized RGB image with the maxmimum possible dynamic range.
    Should work with both, grayscale and RGB images
    """
    amax = np.amax(floatIm)
    amin = np.amin(floatIm)
    tmp = np.copy(floatIm - amin)
    tmp *= 255 / (amax - amin)
    tmp = tmp.astype(np.uint8)
    return tmp


def calculateNDVI(rgb, ir, grayscale=False):
    """
    calculates the NDVI-Picture from the images rgb and IR and returns TWO images:
        ndvi_float are the float-values between -1 and 1
        ndvi is a rescaled uint8 version suitable for saving with cv2.imwrite
    """
#    ir = cv2.cvtColor(ir, cv2.COLOR_RGB2GRAY)
    ir = ir[0:, 0:, 2]

#    ir = cropFrame(ir, 0.1)
#    rgb = cropFrame(rgb, 0.1)

    if grayscale:
        red = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    else:
        red = rgb[0:, 0:, 2]

    ndvi_float = (ir.astype(float) - red.astype(float))
    # +0.0000001 to prevent division by 0
    ndvi_float /= (ir.astype(float) + red.astype(float) + 0.000001)
    ndvi_float = ndvi_float.astype(np.float32)
    ndvi = ndvi_float + 1
    ndvi *= 128
    ndvi = np.around(ndvi)
    ndvi = ndvi.astype(np.uint8)

    return (ndvi, ndvi_float)


def undistortStereoPair(imR, imL):
    """
    undistorts a pair of Stereo images based on the paramers given in paramFile.
    Parameters:
        - imR is the right image
        - imL is the left image
        - paramFilename is the filename, where the Distortion parameters should be saved.
          It must by a .npz-File containing ['PR', 'DCL', 'CML', 'E', 'RR', 'F', 'Q', 'R', 'T', 'RL', 'DCR', 'CMR', 'PL']
          where CMR, CML, DCR and DCL are the matrices and vectors obtained from cv2.calibrate and
          everything else from cv2.stereoRectify
          The current parameters for the raspi-pair are saved in ../data/stereoParams.npz
    """
    pars = np.load(config.get('image processing', 'stereo parameters'))
    h, w = imR.shape[:2]
    mapxR, mapyR = cv2.initUndistortRectifyMap(pars['CMR'], pars['DCR'], pars[
                                               'RR'], pars['PR'], m1type=cv2.CV_32FC1, size=(w, h))
    h, w = imL.shape[:2]
    mapxL, mapyL = cv2.initUndistortRectifyMap(pars['CML'], pars['DCL'], pars[
                                               'RL'], pars['PL'], m1type=cv2.CV_32FC1, size=(w, h))
    undistR = cv2.remap(imR, mapxR, mapyR,
                        cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    undistL = cv2.remap(imL, mapxL, mapyL,
                        cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    return (undistR, undistL)


def calculateDisparityMap(imR, imL):
    """
    calculates the disparity map if imR and imL using the SGBM algorithm
    with the parameters supplied in the config parser thing config.
    THE IMAGES MUST BE PROPERLY ROTATED
    """

    min_disp = config.getint('SGBM', 'minDisparity')
    num_disp = config.getint('SGBM', 'numDisparities')
    stereo = cv2.StereoSGBM_create(
        minDisparity=min_disp,
        numDisparities=num_disp,
        blockSize=config.getint('SGBM', 'blockSize'),
        uniquenessRatio=config.getint('SGBM', 'uniquenessRatio'),
        speckleWindowSize=config.getint('SGBM', 'speckleWindowSize'),
        speckleRange=config.getint('SGBM', 'speckleRange'),
        disp12MaxDiff=config.getint('SGBM', 'disp12MaxDiff'),
        P1=config.getint('SGBM', 'P1'),
        P2=config.getint('SGBM', 'P2'),
        preFilterCap=config.getint('SGBM', 'preFilterCap'),
    )
    # compute disparity\n",
    disparity = stereo.compute(imL, imR).astype(np.float32) / 16.0
    disparity = (disparity - min_disp) / num_disp
    return disparity
#   this should really not be needed, but in fact be bad
#    disparity=floatIm2RGB(disparity)
