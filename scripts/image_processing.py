"""
This module is a collection of the most important image processing functions
needed by the ``measurement`` class.
"""


import cv2
import numpy as np
from config import config
from scipy import ndimage as nd
import scipy as sp
from scipy import signal


def alignImages(im1, im2, showMatches=False, threshold=0.5,
                resizefactor=0.5, append_text_to_statusbar=None):
    """
    expects two images, assumes that both of them are grayscale of both them are RGB.
    Returns an aligned version of im2 in the size of im1

   :param im1:           Any opencv image
   :param im2:           OpenCV image with the same color space
   :param showMatches:   If ``True``, the matches are shown. Default = False
   :param threshold:     Parameter, how good the matches must be to be considered. Default = 0.5 If too low, not enough matches might be found. If too high the alignment may fail
    :param resizefactor:  The factor, by which the images are resized for the sift-detector. Too high -> too much RAM usage. Too low -> not accurate enough
   :rtype: opencv image/numpy array with the same dimensions as ``im2``
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
    crops the image by a constant percentage on each border.

    :param im:        the input image
    :param framesize: is the relative size of the frame, that needs to be cropped away. e.g. 0.1 equals a frame 10% of the size of image
    :rtype: opencv image/numpy array
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

    :param floatIm: Literally any numpy array, but presumably a image that exceeds the
            normal limitations of a opencv image
    :rtype: ``rescaled`` is a rescaled version of the input, having the maximum possible dynamic range. (in a uint8)
    """
    amax = np.amax(floatIm)
    amin = np.amin(floatIm)
    rescaled = np.copy(floatIm - amin)
    rescaled *= 255 / (amax - amin)
    rescaled = rescaled.astype(np.uint8)
    return rescaled


def calculateNDVI(rgb, ir, grayscale=False):
    """
    calculates the NDVI-values from the images rgb and IR

    :param rgb:        The RGB-Image which should be used for the NDVI-Calculation
    :param ir:         The IR-Image which sould be used for the NDVI-Calculation
    :param  grayscale:  specifies, whether `rgb` and `ir` are grayscale images (only one color channel) or rgb images (three color channels). *Make sure, that both images have the same number of color channels*
    :rtype: ``(ndvi, ndvi_float)``: ndvi is a heatmap image of the ndvi-values. ndvi_float is a float-array with the same dimensions as ndvi containing the raw NADVI-Values
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
    ndvi = nd.median_filter(ndvi, 5)
    ndvi = cv2.applyColorMap(ndvi, cv2.COLORMAP_PARULA)
    ndvi_float = nd.median_filter(ndvi_float, 5)

    return (ndvi, ndvi_float)


def calculateRGRatio(im, gamma=1):          #TODO!
    """
    calculates the Ratio of the red and green channel

    :param im:        Obviously the image whose channels get divided, duh... Must be
        BGR. (3 Color channels)
    :param gamma:     exponential to bring out the lower rg-ratios. You probably
        want to choose values below 1
    :rtype: ``(rg, rg_float)``: rg is a heatmap image of the r/g ratios. ndvi_float is a
     float-array with the same dimensions containing the raw values for lookup in the GUI
    """

    # +1 to avoid division by 0... Shouldn't make a big difference in the interesting regions.
    rg_float = im[:, :, 2] / (im[:, :, 1] + 1)
    rg_float = nd.median_filter(rg_float, 5)
    rg = rg_float**gamma
    rg = np.around(rg)
    rg = rg.astype(np.uint8)
    rg = cv2.applyColorMap(rg, cv2.COLORMAP_PARULA)

    return (rg, rg_float)


def deflickerImage(im, column):
    """
    Attempts to get rid of the flickering bars caused by the LEDs. To do so it
    tries to straighten out the brightness values on a supposedly uniformly lit
    calibration bar at the edge of the image.

    :param im:   The image whose flickering bars you want to remove. Can be a grayscale image or RGB. In case of grayscale, every channel is deflickered independently
    :param column:  The number of the column, where the calibration bar is located in the image `im`
    :rtype: ``im_corrected``   A hopefully deflickered version of `im`.
    """
    start = config.getint('image processing', 'deflicker start')
    end = config.getint('image processing', 'deflicker end')

    # creating the flicker profile and smoothing it and setting the edges to the mean
    if (len(im.shape) == 3):
        flicker_profile = im[:, column, 2]
    else:
        flicker_profile = im[:, column]
    mean = np.mean(flicker_profile[start:end])
    flicker_profile[:start] = mean
    flicker_profile[end:] = mean
    flicker_profile = np.float32(flicker_profile) / mean
    flicker_profile = sp.signal.medfilt(flicker_profile, 51)

    # creating the matrix
    correction = np.ones(im.shape)
    flicker_profile = flicker_profile.reshape(len(flicker_profile), 1)
    # I am sure, there are better ways to do this...
    if (len(im.shape) == 3):
        correction[:, :, 0] = correction[:, :, 0] / flicker_profile
        correction[:, :, 1] = correction[:, :, 1] / flicker_profile
        correction[:, :, 2] = correction[:, :, 2] / flicker_profile
    else:
        correction[:, :] = correction / flicker_profile

    im_corrected = np.uint8(
        np.around(np.clip(correction * im.astype(float), 0, 255)))
    return im_corrected


def undistortStereoPair(imR, imL):
    """
    undistorts a pair of Stereo images based on the paramers given in paramFile.
    The distortion parameters are supplied by the config object and stored in
    ../data/stereoParams.npz. This file must be created using the `calibrate_stereo_cameras` Tool

    :param imR:    is the right image
    :param imL:    is the left image
    :rtype: ``(undistR, undistL):`` The undistorted versions of ``imR`` and ``imL``
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
    calculates the disparity map of imR and imL using the SGBM algorithm
    with the parameters supplied in the config parser thing config.
    *The images must be properly rotated and undistorted*

    :param imR: The image taken by the right camera
    :param imL: The image taken by the left camera
    :rtype: ``disparity`` is a grayscale opencv image with the same dimensions as imL and aligned to it (not to imR).
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
