"""
native_stuff.pyx

Contains all Python Wrappers for the functions that had to be implemented in
native C-Code.

    .. note:: If the C-Code changes, the whole module must be recompiled using
        ``setup.py build_ext --inplace`` with thes setup.py script in the
        ``scripts`` folder

.. members::
 - Wrapper for the C-Implementation of the colorMask Function.
 - Wrapper for the RGHistogramEqualizer function.
"""

import cython

# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

# declare the interface to the C code
cdef extern from "cpp_native_stuff.cpp":
    void cpp_colorMask(np.uint8_t * img, np.uint8_t * mask,
                       int m, int n, np.uint8_t * colors, int l, int threshold)


@cython.boundscheck(False)
@cython.wraparound(False)
def colorMask(np.ndarray[np.uint8_t, ndim=3, mode="c"] img,
              np.ndarray[np.uint8_t, ndim=2, mode="c"] mask, colors, int threshold):
    """
    Wrapper for the natively in C implemented cpp_colorMask function.

    Creates a BW-Mask based on the list ``colors`` masking the pixels matching
    one of the colors (within a certain accuracy defined by ``threshold``) white
    and all others black.

    :param img:     The image that should be masked
    :param mask:    The array where the mask is written to.
        .. warning:: if img.shape = [m,n,3], -> mask.shape = [m,n]
    :param colors:  A list of colors that should be masked. The entries must be
        of the form [B,G,R], because that is the pixel format of opencv images
    :param threshold:   The threshold, by which the color value may differ from
    the colors in the list to be still considered to be the *same* color.
    The difference is calculated as the euclidean distance between the colors in
    the BGR-color space.
    :rtype: None. The mask is written to the array ``mask`` which is passed to the
        function.
    """
    cdef int m, n, l
    m, n = img.shape[1], img.shape[0]
    l = len(colors)
    cdef np.ndarray[np.uint8_t, ndim = 2] c = np.empty([l, 3], dtype=np.uint8)

    for i in range(l):
        c[i, 0] = colors[i][0]
        c[i, 1] = colors[i][1]
        c[i, 2] = colors[i][2]

    cpp_colorMask (&img[0, 0, 0], &mask[0, 0], m, n, &c[0, 0], l, threshold)

    return None


# declare the interface to the C code
cdef extern from "cpp_native_stuff.cpp":
    void cpp_RGHistogramEqualizer(np.float32_t * src, np.uint8_t * dst,
                                  int m, int n)


@cython.boundscheck(False)
@cython.wraparound(False)
def RGHistogramEqualizer(np.ndarray[np.float32_t, ndim=2, mode="c"] src,
                         np.ndarray[np.uint8_t, ndim=2, mode="c"] dst):
    """
    Wrapper for the natively in C implemented cpp_RGHistogramEqualizer function.

    Creates a BW-Mask based on the list ``colors`` masking the pixels matching
    one of the colors (within a certain accuracy defined by ``threshold``) white
    and all others black.

    :param src:     The source image whose histogramm needs to be equalized.
                    Must be a np.ndarray with dtype float32(!).
    :param dst:     The destination array. Must be data type uint8
    :rtpye:         np.ndarray with the same dimensions as src and dtype np.uint8.
                    Holds the remapped image, duhh.
    """
    cdef int m, n
    m, n = src.shape[1], src.shape[0]
#    dst = np.empty(src.shape, dtype=np.uint8_t)

    cpp_RGHistogramEqualizer ( &src[0, 0], &dst[0, 0], m, n)

    return None
