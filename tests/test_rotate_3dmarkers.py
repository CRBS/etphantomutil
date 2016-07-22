#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rotate_3dmarkers
----------------------------------

Tests for `rotate_3dmarkers` module.
"""

import sys
import unittest
import os.path
import tempfile
import shutil
import logging

from etspecutil.marker import MarkersList
from etspecutil.marker import MarkersFrom3DMarkersFileFactory
from etspecutil import rotate_3dmarkers
from etspecutil.rotate_3dmarkers import Parameters


class TestRotate3DMarkers(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        theargs = Parameters()
        theargs.loglevel = 'DEBUG'
        rotate_3dmarkers._setup_logging(theargs)
        self.assertEqual(rotate_3dmarkers.logger.getEffectiveLevel(),
                         logging.DEBUG)

        theargs.loglevel = 'INFO'
        rotate_3dmarkers._setup_logging(theargs)
        self.assertEqual(rotate_3dmarkers.logger.getEffectiveLevel(),
                         logging.INFO)

        theargs.loglevel = 'WARNING'
        rotate_3dmarkers._setup_logging(theargs)
        self.assertEqual(rotate_3dmarkers.logger.getEffectiveLevel(),
                         logging.WARNING)

        theargs.loglevel = 'ERROR'
        rotate_3dmarkers._setup_logging(theargs)
        self.assertEqual(rotate_3dmarkers.logger.getEffectiveLevel(),
                         logging.ERROR)

        theargs.loglevel = 'CRITICAL'
        rotate_3dmarkers._setup_logging(theargs)
        self.assertEqual(rotate_3dmarkers.logger.getEffectiveLevel(),
                         logging.CRITICAL)

    def test_parse_arguments(self):
        theargs = rotate_3dmarkers._parse_arguments('hi', ['foo'])
        self.assertEqual(theargs.markerfile, 'foo')
        self.assertEqual(theargs.outfile, None)
        self.assertEqual(theargs.angle, 90)
        self.assertEqual(theargs.width, 1080)
        self.assertEqual(theargs.height, 1080)
        self.assertEqual(theargs.loglevel, 'WARNING')

        targs = rotate_3dmarkers._parse_arguments('hi', ['--angle', '45',
                                                         '--outfile', 'out',
                                                         '--width', '10',
                                                         '--height', '20',
                                                         '--log', 'DEBUG',
                                                         'foo2'])
        self.assertEqual(targs.markerfile, 'foo2')
        self.assertEqual(targs.outfile, 'out')
        self.assertEqual(targs.angle, 45)
        self.assertEqual(targs.width, 10)
        self.assertEqual(targs.height, 20)
        self.assertEqual(targs.loglevel, 'DEBUG')

    def test_rotate_markers_file_outfile_set_to_none(self):
        temp_dir = tempfile.mkdtemp()
        try:
            markerfile = os.path.join(temp_dir, '3Dmarkers.txt')
            markers = MarkersList()
            markers.add_marker(1, 2, 3, 4)
            markers.write_markers_to_file(markerfile)

            theargs = Parameters()
            theargs.outfile = None
            theargs.angle = 90
            theargs.width = 10
            theargs.height = 10
            theargs.markerfile = markerfile
            rotate_3dmarkers.rotate_markers_file(theargs)
            origfile = markerfile + '.orig'
            self.assertTrue(os.path.isfile(origfile))
            fac = MarkersFrom3DMarkersFileFactory(origfile)
            markers = fac.get_markerslist()
            m = markers.get_markers()[0]
            self.assertEqual(m.get_index(), 1)
            self.assertEqual(m.get_x(), 2)
            self.assertEqual(m.get_y(), 3)
            self.assertEqual(m.get_z(), 4)

            self.assertTrue(os.path.isfile(markerfile))
            fac = MarkersFrom3DMarkersFileFactory(markerfile)
            markers = fac.get_markerslist()
            m = markers.get_markers()[0]
            self.assertEqual(m.get_index(), 1)
            self.assertEqual(m.get_x(), 7)
            self.assertEqual(m.get_y(), 2)
            self.assertEqual(m.get_z(), 4)
        finally:
            shutil.rmtree(temp_dir)

    def test_rotate_markers_file_outfile_set(self):
        temp_dir = tempfile.mkdtemp()
        try:
            markerfile = os.path.join(temp_dir, '3Dmarkers.txt')
            markers = MarkersList()
            markers.add_marker(1, 2, 3, 4)
            markers.write_markers_to_file(markerfile)
            outfile = os.path.join(temp_dir, 'out')
            theargs = Parameters()
            theargs.outfile = outfile
            theargs.angle = 90
            theargs.width = 10
            theargs.height = 10
            theargs.markerfile = markerfile
            rotate_3dmarkers.rotate_markers_file(theargs)

            self.assertTrue(os.path.isfile(markerfile))

            fac = MarkersFrom3DMarkersFileFactory(outfile)
            markers = fac.get_markerslist()
            m = markers.get_markers()[0]
            self.assertEqual(m.get_index(), 1)
            self.assertEqual(m.get_x(), 7)
            self.assertEqual(m.get_y(), 2)
            self.assertEqual(m.get_z(), 4)
        finally:
            shutil.rmtree(temp_dir)

    def test_main(self):
        try:
            rotate_3dmarkers.main()
            self.fail('Expected OSError')
        except OSError:
            pass

if __name__ == '__main__':
    sys.exit(unittest.main())
