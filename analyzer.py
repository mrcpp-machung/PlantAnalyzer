#!/usr/bin/env python


from datetime import datetime
from scripts.measurement import measurement
# from scripts.config import config
import os
import time
import argparse


from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf
# from gi.repository import Gdk
import cv2
# import numpy as np

parser = argparse.ArgumentParser(
    description='The glorious plant analyzer')

parser.add_argument("--filename", "-f",
                    help="open a zip file")

args = parser.parse_args()

proj = measurement("mess")
if args.filename:
    proj.open(args.filename)

DEBUG = True


class dummy:
    """
    The big ass class that holds the whole GUI of the *PlantAnalyzer*.

    Only the not self explaining functions like ``append_text_to_statusbar``
    are documented, while it should be obvious what e.g. ``on_button_new_clicked``
    does.
    """

    def append_text_to_statusbar(self, text):
        """
        appends a line of text to the log window at the bottom of the window and
        scrolls to the end of the text buffer displayed in the window.

        :param text:  the string, that should be appended to the log window
        :rtype: None
       """
        iter = self.statusbar_buffer.get_end_iter()
        self.statusbar_buffer.insert(iter, text)
        iter = self.statusbar_buffer.get_end_iter()
        self.statusbar.scroll_to_iter(
            iter, 0.49, use_align=True, xalign=0.0, yalign=0.0)
        while gtk.events_pending():
            gtk.main_iteration_do(False)
            time.sleep(0.01)  # super stupid hack to make the GUI update
            # properly...

    def write_results(self):
        """
        Writes the results of the Total leaf area, the average NDVI value
        and the average R/G ratio to the result view on the right side of the GUI.

        :rtype: None
       """
        string = "Total leaf Area:            " + str(proj.leafArea) + "\n"
        string += "Average NDVI value:        " + str(proj.averageNDVI) + "\n"
        string += "Average red green ration:  " + str(proj.averageRG) + "\n"
        self.resultview_buffer.set_text(string)

    def update_images(self):
        """
        Updates all images in the GUI.

        .. warning:: **Must** be called after the GUI was resized or the images have changed
        or ToggleZoom has been clicked

        :rtype: None
       """
        height = self.imRGB.get_allocation().height
        width = self.imRGB.get_allocation().width

        # only update pictures, when they really exist
        if hasattr(proj, 'imNDVI'):
            cv2.imwrite(proj.NDVIFilename, proj.imNDVI)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(proj.NDVIFilename)
            if self.zoom:
                pixbuf = pixbuf.scale_simple(height, width,
                                             GdkPixbuf.InterpType.BILINEAR)
            self.imNDVI.set_from_pixbuf(pixbuf)

        if hasattr(proj, 'imRG'):
            cv2.imwrite(proj.RGFilename, proj.imRG)
            pixbuf1 = GdkPixbuf.Pixbuf.new_from_file(proj.RGFilename)
            if self.zoom:
                pixbuf1 = pixbuf1.scale_simple(height, width,
                                               GdkPixbuf.InterpType.BILINEAR)
            self.imRG.set_from_pixbuf(pixbuf1)

        if hasattr(proj, 'imRGB'):
            cv2.imwrite(proj.RGBFilename, proj.imRGB)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(proj.RGBFilename)
            pixbuf = pixbuf.scale_simple(height, width,
                                         GdkPixbuf.InterpType.BILINEAR)
            self.imRGB.set_from_pixbuf(pixbuf)

        if hasattr(proj, 'imRed'):
            cv2.imwrite(proj.RedFilename, proj.imRed)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(proj.RedFilename)
            pixbuf = pixbuf.scale_simple(height, width,
                                         GdkPixbuf.InterpType.BILINEAR)
            self.imRed.set_from_pixbuf(pixbuf)

        if hasattr(proj, 'imIR'):
            cv2.imwrite(proj.IRFilename, proj.imIR)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(proj.IRFilename)
            pixbuf = pixbuf.scale_simple(height, width,
                                         GdkPixbuf.InterpType.BILINEAR)
            self.imIR.set_from_pixbuf(pixbuf)

        if hasattr(proj, 'imRight'):
            cv2.imwrite(proj.RightFilename, proj.imRight)


        if hasattr(proj, 'leafMask'):
            cv2.imwrite(proj.leafMaskFilename, proj.leafMask)
#            pixbuf = GdkPixbuf.Pixbuf.new_from_file(proj.IRFilename)
#            pixbuf = pixbuf.scale_simple(height, width,
#                                         GdkPixbuf.InterpType.BILINEAR)
#            self.imIR.set_from_pixbuf(pixbuf)

        # uncomment, if they should be displayed and copy code from above
#        if hasattr(proj,'imLeft'):
#            cv2.imwrite( proj.LeftFilename, proj.imLeft)

#        if hasattr(proj,'imIRsheared'):
#            cv2.imwrite( proj.IRshearedFilename, proj.imIRsheared)

    def on_toggle_zoom_clicked(self, object, data=None):
        if self.zoom is False:
            self.zoom = True
        else:
            self.zoom = False
        self.update_images()

    def on_ndviBox_button_press_event(self, box, event):
        """
        Is called, if the user clicks into the NDVI view. Prints the NDVI value
        of the pixel clicked to the log window on the bottom.

        :rtype: None
       """

#        pixbuf = self.imNDVI.get_pixbuf()
        x = int(event.x)
        y = int(event.y)

#        if pixbuf is not None:
#            ndvi_value = pixbuf.get_pixels()[y * pixbuf.get_rowstride()
#                                             + x * pixbuf.get_n_channels()]
#            ndvi_value = str(ord(ndvi_value))

        if hasattr(proj, 'NDVI_float'):
            fx = float(proj.NDVI_float.shape[1]) / float(self.imNDVI.get_allocation().height)
            fy = float(proj.NDVI_float.shape[0]) / float(self.imNDVI.get_allocation().width)
            if self.zoom is False:
                fx = fy = 1      # to be changed later
            ndvi_value = proj.NDVI_float[int(fy * y), int(fx * x)]
            self.append_text_to_statusbar("NDVI-Value: " + str(ndvi_value) + "\n")
        else:
            print("The NDVI Values are not calculated yet...")

    def on_rgBox_button_press_event(self, box, event):
        """
        Is called, if the user clicks into the RG view. Prints the RG ratio
        of the pixel clicked to the log window on the bottom.

        :rtype: None
       """

        x = int(event.x)
        y = int(event.y)

        if hasattr(proj, 'RG_float'):
            fx = float(proj.RG_float.shape[1]) / float(self.imRG.get_allocation().height)
            fy = float(proj.RG_float.shape[0]) / float(self.imRG.get_allocation().width)
            if self.zoom is False:
                fx = fy = 1      # to be changed later
            rg_value = proj.RG_float[int(fy * y), int(fx * x)]
            self.append_text_to_statusbar("red-green-ratio: " + str(rg_value) + "\n")
        else:
            print("The red green ratios are not calculated yet...")

    def on_button_new_clicked(self, object, data=None):
        print("projectname chooser selected")
        self.projectname_entry.set_text(
            datetime.now().strftime("%Y-%m-%d_%X"))
        self.response = self.projectname_dialog.run()

    def on_button_ok_clicked(self, object, data=None):
        proj.name = self.projectname_entry.get_text()
        proj.IRFilename = "./data/" + proj.name + "IR.jpg"
        proj.RedFilename = "./data/" + proj.name + "Red.jpg"
        proj.RGBFilename = "./data/" + proj.name + "RGB.jpg"
        proj.RightFilename = "./data/" + proj.name + "Right.jpg"
        proj.NDVIFilename = "./data/" + proj.name + "NDVI.jpg"
        proj.RGFilename = "./data/" + proj.name + "RG.jpg"
        proj.DispFilename = "./data/" + proj.name + "Disp.jpg"
        self.append_text_to_statusbar(
            "Set project name to " + proj.name + "\n")
        self.projectname_dialog.destroy()

    def on_projectname_dialog_destroy(self, object, data=None):
        self.projectname_dialog.destroy()

    def on_button_shutter_clicked(self, object, data=None):
        self.append_text_to_statusbar("Taking photos\n")
        proj.takePhotos(statusbar_printer=self.append_text_to_statusbar)
        self.update_images()

    def on_button_analyze_clicked(self, object, data=None):
        self.append_text_to_statusbar("Analyzing the photos. This may take a")
        self.append_text_to_statusbar(" while...\n")
        proj.analyze(statusbar_printer=self.append_text_to_statusbar)
        self.update_images()
        self.write_results()


    def on_window1_destroy(self, object, data=None):
        print("quit with cancel")
        gtk.main_quit()

    def on_gtk_about_activate(self, menuitem, data=None):
        print("about window selected")
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("quit from menu")
        gtk.main_quit()

    def on_resize(self, menuitem):
        #        self.update_images()
        pass

    def on_button_refresh_clicked(self, menuitem, data=None):
        self.update_images()

    def on_button_save_clicked(self, menuitem, data=None):
        proj.save()
        self.append_text_to_statusbar(
            "Saved everything to " + proj.name + ".zip\n")

    def on_gtk_save_activate(self, menuitem, data=None):
        proj.save()
        self.append_text_to_statusbar(
            "Saved everything to " + proj.name + ".zip\n")

    def on_gtk_saveas_activate(self, menuitem, data=None):
        self.fcds = gtk.FileChooserDialog("Save as...", None,
                                          gtk.FileChooserAction.SAVE,
                                          (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
                                           gtk.STOCK_SAVE_AS, gtk.ResponseType.OK))
        self.fcds.set_current_folder(self.current_folder)
        self.fcds.add_filter(self.filefilter)
        self.response = self.fcds.run()

        if self.response == gtk.ResponseType.OK:
            proj.save(self.fcds.get_filename())
            self.append_text_to_statusbar("Saved everything as " +
                                          self.fcds.get_filename() + "\n")
            self.current_folder = self.fcds.get_current_folder()
            self.fcds.destroy()

        if self.response == gtk.ResponseType.CANCEL:
            self.fcds.destroy()

    def on_gtk_open_activate(self, menuitem, data=None):
        self.fcdo = gtk.FileChooserDialog("Open...", None,
                                          gtk.FileChooserAction.OPEN,
                                          (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
                                           gtk.STOCK_OPEN, gtk.ResponseType.OK))
        self.fcdo.set_current_folder(self.current_folder)
        self.fcdo.add_filter(self.filefilter)
        self.response = self.fcdo.run()

        if self.response == gtk.ResponseType.OK:
            proj.open(self.fcdo.get_filename())
            self.append_text_to_statusbar("Opened " +
                                          self.fcdo.get_filename() + "\n")
            self.current_folder = self.fcdo.get_current_folder()
            self.fcdo.destroy()
            self.update_images()
            self.write_results()

        if self.response == gtk.ResponseType.CANCEL:
            self.fcdo.destroy()

    def __init__(self):
        self.gladefile = "analyzer.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.projectname_entry = self.builder.get_object("projectname_entry")

        # retrieve all the GUI-Elements from the builder and embellish them
        self.window = self.builder.get_object("window1")
        self.button_shutter = self.builder.get_object("button_shutter")
        self.button_shutter.set_use_stock(gtk.STOCK_MEDIA_RECORD)
        self.button_shutter.set_label("Take Photos")
        self.button_analyze = self.builder.get_object("button_analyze")
        self.button_analyze.set_use_stock(gtk.STOCK_MEDIA_FORWARD)
        self.button_analyze.set_label("Analyze")
        self.button_save = self.builder.get_object("button_save")
        self.imRGB = self.builder.get_object("imRGB")
        self.imRed = self.builder.get_object("imRed")
        self.imIR = self.builder.get_object("imIR")
        self.imNDVI = self.builder.get_object("imNDVI")
        self.imRG = self.builder.get_object("imRG")
        self.images = self.builder.get_object("images")
        self.grid2 = self.builder.get_object("grid2")
        self.grid2.props.expand = True
        self.statusbar = self.builder.get_object("statusbar")
        self.result_view = self.builder.get_object("result_view")
        self.statusbar_buffer = self.statusbar.get_buffer()
        self.resultview_buffer = self.result_view.get_buffer()
        self.filefilter = gtk.FileFilter()
        self.filefilter.add_pattern("*.zip")
        self.current_folder = os.path.expanduser('~')
        self.aboutdialog = self.builder.get_object("aboutdialog1")
        self.zoom = False

        self.projectname_dialog = self.builder.get_object("projectname_dialog")

        self.window.show()

if __name__ == "__main__":
    main = dummy()
    gtk.main()
