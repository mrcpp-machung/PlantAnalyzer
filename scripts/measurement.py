import cv2
import numpy as np
import leds
import image_processing as IP
from config import config
import os
import shutil
import zipfile
# from time import sleep
# import ConfigParser

raspi2IP = config.get('general', 'raspi2IP')


def status_printer(text, printer=None):
    """
    prints "text" to either the the stdout, or uses the supplied printer(string) function
    print() must take exactly one argument
    """
    if printer is not None:
        printer(text)
    else:
        print(text)


class measurement:
    """
    a class to hold all the informations about a measurement and process them
    member functions:
        look at the source code, or call `help(measurement)`
    variables:
        imRGB:   Those are the images needed
        imRed:  self explanatory
        imIR:   --------""---------
        imNDVI: --------""---------
        imRight: --------""---------
        Disp:   image of the disparity map
        NDVI_float: a huge array with floats made to fool Biologists that they
                    have super precise data (which they don't!)

        a lot of Numbers I don't know about yet
    """

    def __init__(self, name):
        """
        initializes all filenames based on the project name
        """
        self.name = name
        self.IRFilename = "./data/" + self.name + "IR.jpg"
        self.RedFilename = "./data/" + self.name + "Red.jpg"
        self.RGBFilename = "./data/" + self.name + "RGB.jpg"
        self.RightFilename = "./data/" + self.name + "Right.jpg"
        self.NDVIFilename = "./data/" + self.name + "NDVI.jpg"
        self.DispFilename = "./data/" + self.name + "Disp.jpg"
        self.NDVI_floatFilename = "./data/" + self.name + "NDVI_int"

    def takePhotos(self, statusbar_printer=None):
        """
        takes all three photos and saves them to /home/pi/images/<name>.jpg
        variables:
            append_text_to_statusbar: a function that prints text to a
            statusbar. If handed none, the standard print command will be used
       """

        leds.initLEDs()

        # take the RGB picture
        leds.setWhite(100)      # TODO: set this to the right value
        cmd = "/home/pi/bin/takePhoto.py -f " + self.RGBFilename
        cmd += " " + config.get('camera', 'RGB image')
        os.system(cmd)
        leds.setWhite(0)
        status_printer("RGB Photo taken\n", statusbar_printer)

        #  take the Red Picture # change it maybe to the other camera
        leds.setRed(100)
        cmd = "/home/pi/bin/takePhoto.py -f " + self.RedFilename
        cmd += " " + config.get('camera', 'Red image')
        os.system(cmd)
        leds.setRed(0)
        status_printer("Red photo taken\n", statusbar_printer)

        # take the IR picture
        leds.setIR(100)
        cmd = "/home/pi/bin/takePhoto.py -f " + self.IRFilename
        cmd += " " + config.get('camera', 'IR image')
#        cmd = "sshpass -p \"raspberry\" ssh pi@" + raspi2IP
#        cmd += " /home/pi/bin/takePhoto.py -f  /home/pi/tmp1.jpg"
        err = os.system(cmd)
        leds.setIR(0)
        if (err != 0):
            status_printer("Something went wrong while taking the remote photo\n",
                           statusbar_printer)
        else:
            status_printer("IR photo taken\n", statusbar_printer)

        # take the right picture
        leds.setWhite(100)
        cmd = "sshpass -p \"raspberry\" ssh pi@" + raspi2IP
        cmd += " /home/pi/bin/takePhoto.py -f  /home/pi/tmp2.jpg"
        cmd += " " + config.get('camera', 'RGB image')
        err = os.system(cmd)
        leds.setWhite(0)
        if (err != 0):
            status_printer("Something went wrong while taking the remote photo\n",
                           statusbar_printer)
        else:
            status_printer("Right Photo taken\n", statusbar_printer)

        cmd = "sshpass -p \"raspberry\" scp pi@" + raspi2IP + ":/home/pi/tmp2.jpg "
        cmd += self.RightFilename
        err = os.system(cmd)
        if (err != 0):
            status_printer("Something went wrong while retrieving the remote photo.\n",
                           statusbar_printer)
            status_printer(
                "Is the  IP-Adress in /etc/hosts correct?\n", statusbar_printer)
        else:
            status_printer("Right photo retrieved\n", statusbar_printer)

#        cmd = "sshpass -p \"raspberry\" scp pi@" + raspi2IP + ":/home/pi/tmp2.jpg "
#        cmd += self.LeftFilename
#        err = os.system(cmd)
#        if (err != 0):
#            status_printer("Something went wrong while retrieving the remote photo.\n",
#                           statusbar_printer)
#            status_printer(
#                "Is the  IP-Adress in /etc/hosts correct?\n", statusbar_printer)
#        else:
#            status_printer("IR photo retrieved\n", statusbar_printer)

        self.imRGB = cv2.imread(self.RGBFilename)
        self.imRed = cv2.imread(self.RedFilename)
        self.imIR = cv2.imread(self.IRFilename)
        self.imRight = cv2.imread(self.RightFilename)
        self.undistorted = False

    def analyze(self, statusbar_printer=None):
        """
        the name is self explanatory... It undistorts the images and creates
        self.imNDVI and self.NDVI_float
        variables:
            append_text_to_statusbar: a function that prints text to a
            statusbar. If handed none, the standard print command will be used
        """
        # here imRGB doubles as imRight, but is not stored again, as we are
        # going to exclusively use the undistorted images
        if not self.undistorted:
            status_printer("undistorting images...\n", statusbar_printer)
            tmp = self.imRight
            self.imRight, self.imRGB = IP.undistortStereoPair(
                self.imRight, self.imRGB)
            tmp2, self.imIR = IP.undistortStereoPair(tmp, self.imIR)
            tmp2, self.imRed = IP.undistortStereoPair(tmp, self.imRed)
            self.undistorted = True
#        status_printer("aligning images for NDVIcalculations\n",
#                       statusbar_printer)
#        self.imIRsheared = IP.alignImages(self.imRGB, self.imIR)
        status_printer("calculating NDVI Values\n", statusbar_printer)
        (self.imNDVI, self.NDVI_float) = IP.calculateNDVI(self.imRed, self.imIR, grayscale=False)
        status_printer("Calculating disparity map \n", statusbar_printer)
        self.computeDisparity()

    def computeDisparity(self):
        """
        takes only undistorted images!
        computes the disparity map, duh...
        """
        left = cv2.resize(self.imRGB, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        right = cv2.resize(self.imRight, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        left = cv2.transpose(left, None)
        right = cv2.transpose(right, None)
        left = cv2.flip(left, 0)
        right = cv2.flip(right, 0)

        disparity = IP.calculateDisparityMap(right, left)
        disparity = cv2.flip(disparity, 0)
        disparity = cv2.transpose(disparity, None)
#        disparity -= np.amin(disparity)
        disparity = (disparity * 255).astype(np.uint8)
        self.disparity = cv2.resize(disparity, None, fx=2, fy=2, interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.DispFilename, self.disparity)

    def maskLeaves(self):
        """
        creates a bitmask which is 255 where leaves are, and 0 everywhere else
        self.leafMask hast the same dimensions as all other images
        """
        self.leafMask = np.copy(self.imNDVI)    # just create an array of the right size

    def save(self, filename="gurkensalat.zip"):
        """
        saves the images and all the data from the analyzation to a Zip file
        containing the images and a .csv-file with the analyzed values.
        """
        if filename == "gurkensalat.zip":   # nobody will ever call his project gurkensalat,
            filename = self.name + ".zip"   # hopefully... It would cause a really funny error

        if filename[-4:] != ".zip":         # make sure, we have the right filename extension
            filename += ".zip"

        np.save(self.NDVI_floatFilename, self.NDVI_float)

        with open("data.txt", "w") as text_file:
            text_file.write("Average NDVI Value = \n")
            text_file.write("Total Leaf Area = \n")

        file = zipfile.ZipFile(filename, mode='w')
        file.write(self.RGBFilename, "RGB.jpg")
        file.write(self.RedFilename, "Red.jpg")
        file.write(self.IRFilename, "IR.jpg")
        file.write(self.NDVIFilename, "NDVI.jpg")
        file.write(self.RightFilename, "Right.jpg")
        file.write(self.DispFilename, "disparity.jpg")
        file.write(self.NDVI_floatFilename + ".npy", "NDVI_float.npy")
        file.write("data.txt")
        file.close()

    def open(self, filename="mess.zip"):
        """
        opens `filename` (presumably a zip-file created by self.save) and sets all names etc.
        accordingly and opens the images.
        """
        self.name = os.path.basename(filename)[:-4]   # remove the .zip ending.
        self.IRFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "IR.jpg"
        self.RedFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "Red.jpg"
        self.RGBFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "RGB.jpg"
        self.RightFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "Right.jpg"
        self.NDVIFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "NDVI.jpg"
        self.DispFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "Disp.jpg"
        self.NDVI_floatFilename = "/home/pi/PlantAnalyzer/data/" + self.name + "NDVI_float"
        print(self.name)

        file = zipfile.ZipFile(filename, mode='r')
        RGB = file.extract("RGB.jpg")
        Red = file.extract("Red.jpg")
        NDVI = file.extract("NDVI.jpg")
        IR = file.extract("IR.jpg")
        Right = file.extract("Right.jpg")
        disparity = file.extract("disparity.jpg")
        NDVI_float = file.extract("NDVI_float.npy")
        os.rename(RGB, self.RGBFilename)
        os.rename(Red, self.RedFilename)
        os.rename(NDVI, self.NDVIFilename)
        os.rename(IR, self.IRFilename)
        os.rename(Right, self.RightFilename)
        os.rename(disparity, self.DispFilename)
        os.rename(NDVI_float, self.NDVI_floatFilename + ".npy")

        self.imRGB = cv2.imread(self.RGBFilename)
        self.imRed = cv2.imread(self.RedFilename)
        self.imNDVI = cv2.imread(self.NDVIFilename, 0)
        self.imIR = cv2.imread(self.IRFilename)
        self.imRight = cv2.imread(self.RightFilename)
        self.disparity = cv2.imread(self.DispFilename, 0)
        self.NDVI_float = np.load(self.NDVI_floatFilename + ".npy")

        self.undistorted = True
