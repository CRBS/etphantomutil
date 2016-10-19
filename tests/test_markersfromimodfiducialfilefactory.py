#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
tests MarkersFromIMODFiducialFileFactory
----------------------------------

Tests for `etspecutil` module.
"""


import sys
import unittest
import os.path
import tempfile
import math
import shutil

from etspecutil.marker import Marker
from etspecutil.marker import MarkersList

from etspecutil.marker import MarkersFromIMODFiducialFileFactory
from etspecutil.marker import InvalidAngleError
from etspecutil.marker import CommonByIndexMarkersListFilter


class TestMarkersFromIMODFiducialFileFactory(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_markers_no_fiducial_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mfac = MarkersFromIMODFiducialFileFactory(None)
            mlist = mfac.get_markers()
            self.assertEqual(mlist.get_markers(), [])
            non_exist_file = os.path.join(temp_dir,'foo.txt')
            mfac = MarkersFromIMODFiducialFileFactory(non_exist_file)
            mlist = mfac.get_markers()
            self.assertEqual(mlist.get_markers(), [])
        finally:
            shutil.rmtree(temp_dir)

    def test_get_set_fiducial_file(self):
        mfac = MarkersFromIMODFiducialFileFactory(None)
        self.assertEqual(mfac.get_fiducial_file(), None)
        mfac.set_fiducial_file('yo')
        self.assertEqual(mfac.get_fiducial_file(), 'yo')

        mfac = MarkersFromIMODFiducialFileFactory('hi')
        self.assertEqual(mfac.get_fiducial_file(), 'hi')
        mfac.set_fiducial_file(None)
        self.assertEqual(mfac.get_fiducial_file(), None)

    def test_get_markers_model2point_fails(self):
        temp_dir = tempfile.mkdtemp()
        try:
            fid_file = os.path.join(temp_dir, 'somefile.txt')
            open(fid_file, 'a').close()
            mfac = MarkersFromIMODFiducialFileFactory(fid_file)
            mfac.set_model2point_binary('false')
            try:
                mlist = mfac.get_markers()
                self.fail('Expected exception')
            except Exception as e:
                self.assertTrue(str(e).startswith('Non zero exit code when '
                                                  'running : false -float '
                                                  '-contour ' + fid_file))
        finally:
            shutil.rmtree(temp_dir)



if __name__ == '__main__':
    sys.exit(unittest.main())
