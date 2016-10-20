#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tiltseries
----------------------------------

Tests for `tiltseries` module.
"""

import sys
import unittest
import os.path
import tempfile
import shutil
import logging

from etspecutil.tiltseries import TiltSeriesCreator
from etspecutil.rotate_3dmarkers import Parameters


class TestTiltSeriesCreator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_valid_args_for_constructor(self):
        theargs = Parameters()
        theargs.outputdirectory = 'out'
        theargs.inputmrcfile = 'input'
        theargs.begintilt = '-60'
        theargs.endtilt = '60'
        theargs.tiltshift = '2'
        theargs.cores = '1'
        theargs.mpiexec = ''
        theargs.nummarkers = '20'
        theargs.bottommarkersize = '7'
        theargs.topmarkersize = '9'
        theargs.markernoise  = '1'
        theargs.aparam = '0.98'
        theargs.markera = '0.2'
        theargs.shrinkage = '1'
        theargs.projmaxangle = '2'
        theargs.numrotations = '2'
        theargs.etspecbin = '/./foo'
        theargs.rotationangles = ''
        return theargs

    def test_constructor(self):

        theargs = Parameters()
        try:
            TiltSeriesCreator(theargs)
            self.fail('Expected TypeError')
        except AttributeError:
            pass

        theargs = self._get_valid_args_for_constructor()
        ts = TiltSeriesCreator(theargs)
        self.assertEqual(ts._etspecbin, '/foo')
        self.assertEqual(ts._rawrotationlist, [90.0])

    def test_initialize(self):
        temp_dir = tempfile.mkdtemp()
        try:
            theargs = self._get_valid_args_for_constructor()
            subdir = os.path.join(temp_dir, 'foo')
            theargs.outputdirectory = subdir
            theargs.numrotations = ''
            theargs.rotationangles = '45,90,135'
            ts = TiltSeriesCreator(theargs)
            ts.initialize()
            self.assertTrue(os.path.isdir(subdir))
            self.assertTrue(os.getcwd().endswith('foo'))
            self.assertEqual(ts._rotationangles, [0.0, 45.0, 90.0, 135.0])

        finally:
            shutil.rmtree(temp_dir)

    def test_get_methods(self):
        temp_dir = tempfile.mkdtemp()
        try:
            theargs = self._get_valid_args_for_constructor()
            subdir = os.path.join(temp_dir, 'foo')
            theargs.outputdirectory = subdir
            theargs.numrotations = '4'
            ts = TiltSeriesCreator(theargs)
            ts._workdir = temp_dir
            self.assertEqual(ts._get_warpz_dir(),
                             os.path.join(temp_dir,
                                          TiltSeriesCreator.WARPZ_DIR_NAME))
            self.assertEqual(ts._get_marker_dir(),
                             os.path.join(temp_dir,
                                          TiltSeriesCreator.MARKER_DIR_NAME))
            self.assertEqual(ts._get_projection_dir(),
                             os.path.join(temp_dir,
                                          TiltSeriesCreator.
                                          PROJECTION_DIR_NAME))
            self.assertEqual(ts._get_tracking_dir(),
                             os.path.join(temp_dir,
                                          TiltSeriesCreator.TRACKING_DIR_NAME))
            self.assertEqual(ts._get_result_dir(),
                             os.path.join(subdir,
                                          TiltSeriesCreator.RESULT_DIR_NAME))
        finally:
            shutil.rmtree(temp_dir)
if __name__ == '__main__':
    sys.exit(unittest.main())
