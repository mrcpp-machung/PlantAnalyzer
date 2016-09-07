
"""
colorMask.pyx

C++-Implementation of the colorMask Function.
Main Purpose is to learn the correct usage of Cython

"""

import cython

# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

# declare the interface to the C code
cdef extern from "cpp_native_stuff.cpp":
    void cpp_colorMask(np.uint8_t * img, np.uint8_t * mask,
                       int m, int n, np.uint8_t * colors, int l, int threshold)

# cdef extern void cpp_colorMask(np.uint8_t* img, int m, int n,
# np.uint8_t* colors, int l, int threshold)


@cython.boundscheck(False)
@cython.wraparound(False)
def colorMask(np.ndarray[np.uint8_t, ndim=3, mode="c"] img,
              np.ndarray[np.uint8_t, ndim=2, mode="c"] mask, colors, int threshold):
    """
    Comment stuff...
    """
    cdef int m, n, l
    m, n = img.shape[1], img.shape[0]
    l = len(colors)
    cdef np.ndarray[np.uint8_t, ndim = 2] c = np.empty([l, 3], dtype=np.uint8)

    for i in range(l):
        c[i, 0] = colors[i][0]
        c[i, 1] = colors[i][1]
        c[i, 2] = colors[i][2]

    cpp_colorMask ( &img[0, 0, 0], &mask[0, 0], m, n, &c[0, 0], l, threshold)

    return None
