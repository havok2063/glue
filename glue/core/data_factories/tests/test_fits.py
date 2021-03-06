from __future__ import absolute_import, division, print_function

import os
from copy import deepcopy
from collections import namedtuple

import numpy as np
from numpy.testing import assert_array_equal

from glue.core import data_factories as df

from glue.tests.helpers import (requires_astropy, requires_astropy_ge_04,
                                make_file)

from ..fits import fits_reader


DATA = os.path.join(os.path.dirname(__file__), 'data')

Expected = namedtuple('Expected', 'shape, ndim')


def _assert_equal_expected(actual, expected):
    assert len(actual) == len(expected)
    for d in actual:
        e = expected[d.label]
        assert e.shape == d.shape
        assert e.ndim == d.ndim


@requires_astropy
def test_container_fits():

    from astropy.io import fits

    expected = {
        'generic[ATAB]': Expected(
            shape=(20,),
            ndim=1
        ),
        'generic[TWOD]': Expected(
            shape=(4, 5),
            ndim=2
        ),
        'generic[ONED]': Expected(
            shape=(20,),
            ndim=1
        ),
        'generic[THREED]': Expected(
            shape=(2, 2, 5),
            ndim=3
        )
    }

    # Make sure the factory gets used

    d_set = df.load_data(os.path.join(DATA, 'generic.fits'),
                         factory=df.fits_reader)

    _assert_equal_expected(d_set, expected)

    # Check that fits_reader takes HDUList objects

    hdulist = fits.open(os.path.join(DATA, 'generic.fits'))
    d_set = fits_reader(hdulist)

    _assert_equal_expected(d_set, expected)

    # Sometimes the primary HDU is empty but with an empty array rather than
    # None

    hdulist[0].data = np.array([])
    d_set = fits_reader(hdulist)

    _assert_equal_expected(d_set, expected)

    # Check that exclude_exts works

    d_set = fits_reader(hdulist, exclude_exts=['TWOD'])
    expected_reduced = deepcopy(expected)
    expected_reduced.pop('generic[TWOD]')

    _assert_equal_expected(d_set, expected_reduced)


@requires_astropy
def test_auto_merge_fits():

    from astropy.io import fits

    expected = {
        'HDUList[A]': Expected(
            shape=(3, 4),
            ndim=2
        ),
        'HDUList[B]': Expected(
            shape=(3, 4),
            ndim=2
        )
    }

    # Check that merging works

    data = np.ones((3, 4))
    hdu1 = fits.ImageHDU(data)
    hdu1.name = 'a'
    hdu2 = fits.ImageHDU(data)
    hdu2.name = 'b'
    hdulist = fits.HDUList([hdu1, hdu2])

    d_set = fits_reader(hdulist)

    _assert_equal_expected(d_set, expected)

    expected = {
        'HDUList[A]': Expected(
            shape=(3, 4),
            ndim=2
        ),
    }

    d_set = fits_reader(hdulist, auto_merge=True)

    _assert_equal_expected(d_set, expected)

    d_set[0].get_component('A')
    d_set[0].get_component('B')


@requires_astropy
def test_fits_gz_factory():
    data = b'\x1f\x8b\x08\x08\xdd\x1a}R\x00\x03test.fits\x00\xed\xd1\xb1\n\xc20\x10\xc6q\x1f\xe5\xde@ZA]\x1cZ\x8d\x10\xd0ZL\x87\xe2\x16m\x0b\x1d\x9aHR\x87n>\xba\xa5".\tRq\x11\xbe_\xe6\xfb\x93\xe3\x04\xdf\xa7;F\xb4"\x87\x8c\xa6t\xd1\xaa\xd2\xa6\xb1\xd4j\xda\xf2L\x90m\xa5*\xa4)\\\x03D1\xcfR\x9e\xbb{\xc1\xbc\xefIcdG\x85l%\xb5\xdd\xb5tW\xde\x92(\xe7\x82<\xff\x0b\xfb\x9e\xba5\xe7\xd2\x90\xae^\xe5\xba)\x95\xad\xb5\xb2\xfe^\xe0\xed\x8d6\xf4\xc2\xdf\xf5X\x9e\xb1d\xe3\xbd\xc7h\xb1XG\xde\xfb\x06_\xf4N\xecx Go\x16.\xe6\xcb\xf1\xbdaY\x00\x00\x00\x80?r\x9f<\x1f\x00\x00\x00\x00\x00|\xf6\x00\x03v\xd8\xf6\x80\x16\x00\x00'

    with make_file(data, '.fits.gz') as fname:
        d = df.load_data(fname)
        assert df.find_factory(fname) is df.fits_reader

    assert_array_equal(d['PRIMARY'], [[0, 0], [0, 0]])


@requires_astropy
def test_casalike():
    data = b'x\xda\xed\x98Qo\xa3F\x10\xc7\xfbQ\xe6\xcd\x89\xce`v\xd9] R\x1f0\xde$$\xd8\xf8\x80Xq_*.!\xa9%\x1b\xa7@zM?}w\xc1v.\x97\xf8\xae\xc6\xfb\xd0\x07\xfe\xf2\x83e\xc9?\r\xf3\x1fvf6\xf6\xc7\xd3\x80\x03\xfc\n\x1f(\x81\x01\xdc\xad\xf3\x87u\xb1*\xa1Z\xc3\xb9\x9f\xc4PVi~\x9f\x16\xf7\xf0\xa1\x86~2\xf5o?\xe4i\x8c\x08^Z\x14\xe9\x0b\xdc\xa7U\n\xd5\xcbS\x06?\xd1\xc4\xbd\xf5c\xd8\x13\x9f\xe4\xe5\xcf\xab/Y\x01\xeb\x87-y\xb1\xca\xf2r\xb1\xce\xcb\xfd<\xb4\x87\x87\xe1`\xd5<\xac\x98g*\xe6\x91\xbd\xf9;X\xc3\xb1{\x05\x1b?\x98\xce,\xc2lF\x0cj:\x84kF+\x9e?y\xe5\x99\x14[\x84\xda\x98\x98\x8e\xd1\x927ua\xc3\xd3\x88Nm\xdbf\xb6i"\xc7p\xf8\'\x03\xb5\xe0%\xf3)\xafy=?\xafdeU/=h\xafpx\xc5\xbd\xa4\xe1y\x00&\xc1p\x0cN\xb9\x867\x13?i\x9e\xf7j>\x18rw\xfc&\xbe\xc1\xb0X<\xfeQ\xe5YY\xc2\xc9\xd3\xe2\xefly\n\xcf\xf9\xa2\xda\xcb\xe3\x9fo\xfcIx[\xfb\x8bu\xe3\x1b\t?\xcc\xc3\xe3\x8b\xdc\x11\x8f\xe7\xb1\x8c\xef\xfc\x9a\xd6?\x1d\x95\xbf \x9cLCq\x00\xca\xf8\x90n\xbf\x8d\xaf\xc5\xfb\x16\xb8\xc9\x8e\xc7\x04\xcfa\xc8\xa0\x94:\x94\xb5\xab\xbf\xa9g\x18H|\x9a\xf8\xbe\xcb\x9f\xd1\x8e\x877<C\x11\xcfT\xcc#\x8ay"\x7fX%\x0foxH]\xfe\xb0\xe2\xfca\xc5\xf93\x15\xe7\xcfT\\\x7f\xa6J?\x88\xe2\xf8D\xfe\x88\xe2\xfc\x11\xc5\xf9#\x8a\xeb\x8f\xa8\xf2\xc3\x93\xfd\xb7\x9e\xd7z\x91\xabiZ\xecO\x8e:\xef\xbdh\xe6\x06\x9b\xf9\x8f\x8a\xf9\xc5\xc0\x88 f!j\xb4;\x9f\xbd\x11\x0f\x92\x86\xa71\xdd!\xaf\x12\xf3\x0bm\x13\x9f\x18\x9fw\xf1!\xf3\xd8~\xe4\xc9~\xde\xe4\xef>{<\xbe_\xd6~\xd4\xf3no\xc4=E~`P\xd6/k?v<E~`\xc5~`\xc5~\xd4\xfbBo\x16N\x93\xe3y\xd2\x8ff\xff\xd0\xf0n\x1e\xc2\x04!\xf1\xbc\xb4\xa5\x1f\x9b}\xa69\x0f\x10c\x16\xc3\xd4\x12<\xd2\xd2\x8f7\xbc#\xcf\x17\xe9G\x93\xbf\xd5\xa0T\xe4G\xbdo\xf5\xe2$\xbc\xe6\xb1\n?\x88\xc2\xe7\x95~\xa8\xe4I?\x88b?\x9a\xfcm\x7f:*\x7f\xd3\x19\xfe\x1dm\xf6K%\xfdM\xf0\xb0B^\xc4\xe3\xe4<\xfa\\\xf3L\x9dP\x87\x99\xf6\x96\x87\x0c\x18DYY\xc1y\x91\xfd\xf9\x9c\xe5w/pr\xf9\xcf\xe9\x0fy\xf1\x94{\x9b\xfdh\xe8Fs\x8fO\x927\xfb[\xfc\x94\xddUE\xba\x84"{\xc8\n\xc1\xcc\xe0\xa1HW{\xefa\xdc \x91\x15\xb8\x8d\x8fa\xdb\xc2\x98"j\xa3&>wYeE\x9eV\x12\xb3\r\xf2\x15\xfdW\xba|\xce\xde\xf1\xe4\x05\xd1\x9ez\xf9\t\xaf\xde8\xdf\xf0f<\x88\xf8\xf9\xde\xfb\x92\x01\x82 \x8e\xfa\xe2\xdb%\x0f\xfa`\x8a\xfd;\xee\xc3\'L\x19D\xe9\xfdb\xfd\xbe\xfe\xc2\xf1X\xe4\x0c\xee\xd22\xbd[\x17\x19\xe4\xeb\\\xdb]y=\x97\xe9cv\x06D@G}\xa0p\xc1\xc3>0\x88\xc3\x9b>Xp!\xf2\xf4\xee\n\x8d\x07<\xf6\xc2\xa9\xf0\x83\xcf\x02\xf7\xe8z\x16\xf1\xf3h\xc6#\xd9\x7f\x0b\x1d\xdc\x95\x8c\x0c\xdc\xdd\xb7\xeb\xeci\x99\x1dpC1r\x13\xae\t\xa8\xe0a\x03!M|\xb0\x95\x18\xe8\x8c\x18g\x86\xa5\xd3\xda\x9a\x03"N\xfc\xf1v?\xbfI<P\xf1\xbc\x91\x0b\xea\xe65\xc1\x13s\x8b\xbayC\xf0D\x11h\xb7\xb2_"\x9d\x89\x14R\xd1\xdfL\xf1\x9a\x08\x1ek\xcd\x9bK\x1e\xd5\r\x82\x1c\xdbvlf0v\x14\xef\xb7\xe6\xfd\xa5\x94\xd8\x96\x83Mfc\xd4\x8e\'\xeb\xa5\xb9_\x93\xf5\x82\xc5L%J&A\xd6\x191\xcf(\xd6\x19\xa5u\xbd\x0cF\xf2\x15\xae\xef\x8b\x1f\x16\xcb\x0c\xbe\xa6%|-\x16U\x95\xe5\xdf\xc5\x17\xf9\x17\xf2\x06P\xf0<7v\xe5\x19\xa3\x1bp"\xde\xb8/\xe2o\x05r\x18\xc3\xa7\x07T\xd0\xa5/\xdan4\x87\x1a\x16\'n\x94@\x10^$\xee0\xe0\xad\xea\x8fOF\xd0\xa9S\xa7N\x9d:u\xea\xd4\xa9\xd3\xffE\xbft\xea\xd4\xa9S\xa7N\x9d:u\xea\xd4\xe9?\xeb_\xdc?$\x07'
    with make_file(data, '.fits', decompress=True) as fname:
        assert df.is_casalike(fname)
        d = df.load_data(fname, factory=df.casalike_cube)

    assert d.shape == (1, 2, 2, 2)
    d['STOKES 0']
    d['STOKES 1']
    d['STOKES 2']
    d['STOKES 3']

# zlib-compressed
TEST_FITS_DATA = b'x\x9c\xed\xd0\xb1\n\xc20\x14\x85\xe1\xaa/r\xde@\x8a\xe2\xe6\xa0X!\xa0\xa5\xd0\x0c]\xa3m\xa1C\x13I\xe2\xd0\xb7\xb7b\xc5\xa1)\xe2\xe6p\xbe\xe5N\xf7\xe7rsq\xceN\t\xb0E\x80\xc4\x12W\xa3kc[\x07op\x142\x87\xf3J\x97\xca\x96\xa1\x05`/d&\x8apo\xb3\xee{\xcaZ\xd5\xa1T^\xc1w\xb7*\\\xf9Hw\x85\xc81q_\xdc\xf7\xf4\xbd\xbdT\x16\xa6~\x97\x9b\xb6\xd2\xae1\xdaM\xf7\xe2\x89\xde\xea\xdb5cI!\x93\xf40\xf9\xbf\xdf{\xcf\x18\x11\x11\x11\x11\xfd\xad\xe8e6\xcc\xf90\x17\x11\x11\x11\x11\x11\x11\x8d<\x00\x7fy\x7f\xbc'


@requires_astropy
def test_fits_image_loader():
    with make_file(TEST_FITS_DATA, '.fits', decompress=True) as fname:
        d = df.load_data(fname)
        assert df.find_factory(fname) is df.fits_reader
    assert_array_equal(d['PRIMARY'], [1, 2, 3])


@requires_astropy
def test_fits_uses_mmapping():
    with make_file(TEST_FITS_DATA, '.fits', decompress=True) as fname:
        d = df.load_data(fname)
        assert df.find_factory(fname) is df.fits_reader
    assert not d['PRIMARY'].flags['OWNDATA']


@requires_astropy_ge_04
def test_fits_catalog_factory():
    data = b'\x1f\x8b\x08\x08\x19\r\x9cQ\x02\x03test.fits\x00\xed\xd7AO\x830\x18\xc6\xf1\xe9\'yo\x1c\'\x1c\x8c\x97\x1d\x86c\xa6\x911"5\xc1c\x91n\x92\x8cBJ\x97\xb8o\xef\x06\xd3\x98H\xdd\x16\x97]|~\x17\x12H\xfeyI{h\x136\x8b\xc3\x80hD=8\r\xe9\xb5R\x8bJ\x97\r\x99\x8a\xa6\x8c\'\xd4\x18\xa1r\xa1s\xea\xe53\x1e\xb3\xd4\xd2\xbb\xdb\xf6\x84\xd6bC\xb90\x82\xcc\xa6\x96t@4NYB\x96\xde\xcd\xb6\xa7\xd6e&5U\x8b\xcfrQJ\xd5\x14\x95jz{A\xca\x83hb\xfd\xdf\x93\xb51\x00\x00\x00\x00\xf87v\xc7\xc9\x84\xcd\xa3\x119>\x8b\xf8\xd8\x0f\x03\xe7\xdb\xe7!e\x85\x12zCFd+I\xf2\xddt\x87Sk\xef\xa2\xe7g\xef\xf4\xf3s\xdbs\xfb{\xee\xed\xb6\xb7\x92ji\xdev\xbd\xaf\x12\xb9\x07\xe6\xf3,\xf3\xb9\x96\x9eg\xef\xc5\xf7\xf3\xe7\x88\x1fu_X\xeaj]S-\xb4(\xa5\x91\xba\xff\x7f\x1f~\xeb\xb9?{\xcd\x81\xf5\xe0S\x16\x84\x93\xe4\x98\xf5\xe8\xb6\xcc\xa2\x90\xab\xdc^\xe5\xfc%\x0e\xda\xf5p\xc4\xfe\x95\xf3\x97\xfd\xcc\xa7\xf3\xa7Y\xd7{<Ko7_\xbb\xbeNv\xb6\xf9\xbc\xf3\xcd\x87\xfb\x1b\x00\x00\xc0\xe5\r:W\xfb\xe7\xf5\x00\x00\x00\x00\x00\x00\xac>\x00\x04\x01*\xc7\xc0!\x00\x00'
    with make_file(data, '.fits') as fname:
        d = df.load_data(fname)
        assert df.find_factory(fname) is df.fits_reader

    assert_array_equal(d['a'], [1])
    assert_array_equal(d['b'], [2])


@requires_astropy
def test_fits_compressed():
    # Regression test for bug that caused images with compressed image HDUs
    # to not be read
    d = df.load_data(os.path.join(DATA, 'compressed_image.fits'),
                     factory=df.fits_reader)
    assert d.ndim == 2
