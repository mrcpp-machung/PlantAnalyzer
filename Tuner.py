#!/usr/bin/env python

# import sys
import argparse
from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf
# from gi.repository import Gdk
import cv2
import numpy as np
import scripts.image_processing as IP
# from repository import Gtk as gtk

parser = argparse.ArgumentParser(
    description='SGBM Tuner, useful for testing values')
parser.add_argument("--right", "-r", default="right.jpg",
                    help="right image filename")

parser.add_argument("--left", "-l", default="left.jpg",
                    help="left image filename")

args = parser.parse_args()

imR = cv2.imread(args.right, 0)
imL = cv2.imread(args.right, 0)


class dummy:

    def calculateDisparity(self):
        minDisp = self.minDisparity.get_value()
        numDisp = self.numDisparities.get_value()
        stereo = cv2.StereoSGBM_create(
            minDisparity=int(minDisp),
            numDisparities=int(numDisp),
            blockSize=int(self.blockSize.get_value()),
            uniquenessRatio=int(self.uniquenessRatio.get_value()),
            speckleWindowSize=int(self.speckleWindowSize.get_value()),
            speckleRange=int(self.speckleRange.get_value()),
            disp12MaxDiff=int(self.disp12MaxDiff.get_value()),
            P1=int(self.P1.get_value()),
            P2=int(self.P2.get_value()),
            #            preFilterCap = int(self.preFilterCap.get_value()),
        )
        print(int(self.minDisparity.get_value()))
        print(int(self.numDisparities.get_value()))
        print(int(self.blockSize.get_value()))
        print(int(self.P1.get_value()))
        print(int(self.P2.get_value()))
        print(int(self.disp12MaxDiff.get_value()))
        print(int(self.preFilterCap.get_value()))
        print(int(self.uniquenessRatio.get_value()))
        print(int(self.speckleWindowSize.get_value()))
        print(int(self.speckleRange.get_value()))
        kernel = np.ones((12,12),np.uint8)

        disparity = stereo.compute(imL, imR).astype(np.float32) / 16.0
        disparity = (disparity - minDisp) / numDisp
#        print(np.amax(disparity))
#        print(np.amin(disparity))
#        print(disparity[500, 500])
#        cv2.startWindowThread()
#        cv2.namedWindow('disp', cv2.WINDOW_NORMAL)
#        cv2.imshow('disp', disparity)
        disparity = IP.floatIm2RGB(disparity)
        cv2.imwrite("disparity.jpg", disparity)

    def update_images(self):
        height = 0.8 * self.leftImage.get_allocation().height
        width = 0.8 * self.leftImage.get_allocation().width

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(args.right)
        pixbuf = pixbuf.scale_simple(height, width,
                                     GdkPixbuf.InterpType.BILINEAR)
        self.rightImage.set_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(args.left)
        pixbuf = pixbuf.scale_simple(height, width,
                                     GdkPixbuf.InterpType.BILINEAR)
        self.leftImage.set_from_pixbuf(pixbuf)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file("disparity.jpg")
        pixbuf = pixbuf.scale_simple(height, width,
                                     GdkPixbuf.InterpType.BILINEAR)
        self.disparityMap.set_from_pixbuf(pixbuf)

    def on_slider_changed(self, object, data=None):
        self.calculateDisparity()
        self.update_images()

    def on_window1_destroy(self, object, data=None):
        print("quit with cancel")
        gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("quit from menu")
        gtk.main_quit()

    def on_resize(self, menuitem):
        #        self.update_images()
        pass

    def __init__(self):
        self.gladefile = "Tuner.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.minDisparity = self.builder.get_object("minDisparity")
        self.numDisparities = self.builder.get_object("numDisparities")
        self.blockSize = self.builder.get_object("blockSize")
        self.P1 = self.builder.get_object("P1")
        self.P2 = self.builder.get_object("P2")
        self.disp12MaxDiff = self.builder.get_object("disp12MaxDiff")
        self.preFilterCap = self.builder.get_object("preFilterCap")
        self.uniquenessRatio = self.builder.get_object("uniquenessRatio")
        self.speckleWindowSize = self.builder.get_object("speckleWindowSize")
        self.speckleRange = self.builder.get_object("speckleRange")
        self.leftImage = self.builder.get_object("leftImage")
        self.rightImage = self.builder.get_object("rightImage")
        self.disparityMap = self.builder.get_object("disparityMap")
#        self.calculateDisparity()
#        self.update_images()

        # retrieve all the GUI-Elements from the builder and embellish them

        self.window = self.builder.get_object("window1")
        self.window.show()

if __name__ == "__main__":
    main = dummy()
    gtk.main()
