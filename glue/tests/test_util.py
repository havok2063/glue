import unittest

import numpy as np

import glue
from glue.util import *


class TestRelim(unittest.TestCase):
    pass


class TestFileFormat(unittest.TestCase):

    def test_gz(self):
        fmt = file_format('test.tar.gz')
        self.assertEquals(fmt, 'tar')

    def test_normal(self):
        fmt = file_format('test.data')
        self.assertEquals(fmt, 'data')

    def test_underscores(self):
        fmt = file_format('test_file.fits_file')
        self.assertEquals(fmt, 'fits_file')

    def test_multidot(self):
        fmt = file_format('test.a.b.c')
        self.assertEquals(fmt, 'c')

    def test_nodot(self):
        fmt = file_format('test')
        self.assertEquals(fmt, '')


class TestPointContour(unittest.TestCase):
    def test(self):
        data = np.array([ [0, 0, 0, 0],
                          [0, 2, 3, 0],
                          [0, 4, 2, 0],
                          [0, 0, 0, 0] ])
        xy = point_contour(2, 2, data)
        x = np.array([2., 2. + 1./3., 2., 2., 1, .5, 1, 1, 2])
        y = np.array([2./3., 1., 2., 2., 2.5, 2., 1., 1., 2./3])

        np.testing.assert_array_almost_equal(xy[:, 0], x)
        np.testing.assert_array_almost_equal(xy[:, 1], y)


if __name__ == "__main__":
    unittest.main()