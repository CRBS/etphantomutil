#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_create_tiltseries
----------------------------------

Tests for `create_tiltseries` module.
"""

import sys
import unittest
import os.path
import tempfile
import shutil
import logging

from etspecutil.marker import MarkersList
from etspecutil.marker import MarkersFrom3DMarkersFileFactory
from etspecutil import create_tiltseries
from etspecutil.rotate_3dmarkers import Parameters


class TestCreateTiltSeries(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        theargs = Parameters()
        theargs.loglevel = 'DEBUG'
        create_tiltseries._setup_logging(theargs)
        self.assertEqual(create_tiltseries.logger.getEffectiveLevel(),
                         logging.DEBUG)

        theargs.loglevel = 'INFO'
        create_tiltseries._setup_logging(theargs)
        self.assertEqual(create_tiltseries.logger.getEffectiveLevel(),
                         logging.INFO)

        theargs.loglevel = 'WARNING'
        create_tiltseries._setup_logging(theargs)
        self.assertEqual(create_tiltseries.logger.getEffectiveLevel(),
                         logging.WARNING)

        theargs.loglevel = 'ERROR'
        create_tiltseries._setup_logging(theargs)
        self.assertEqual(create_tiltseries.logger.getEffectiveLevel(),
                         logging.ERROR)

        theargs.loglevel = 'CRITICAL'
        create_tiltseries._setup_logging(theargs)
        self.assertEqual(create_tiltseries.logger.getEffectiveLevel(),
                         logging.CRITICAL)

    def test_parse_arguments(self):
        theargs = create_tiltseries._parse_arguments('hi', ['inputmrc',
                                                            'outdir'])
        self.assertEqual(theargs.inputmrcfile, 'inputmrc')
        self.assertEqual(theargs.outputdirectory, 'outdir')
        self.assertEqual(theargs.begintilt, -60)
        self.assertEqual(theargs.endtilt, 60)
        self.assertEqual(theargs.tiltshift, 2)
        self.assertEqual(theargs.loglevel, 'WARNING')
        self.assertEqual(theargs.nummarkers, 20)
        self.assertEqual(theargs.bottommarkersize, 7)
        self.assertEqual(theargs.topmarkersize, 9)
        self.assertEqual(theargs.markernoise, 0)
        self.assertEqual(theargs.aparam, 0.2)
        self.assertEqual(theargs.markera, 0.98)
        self.assertEqual(theargs.shrinkage, 0.0005)
        self.assertEqual(theargs.projmaxangle, 0.0004)
        self.assertEqual(theargs.numrotations, '')
        self.assertEqual(theargs.rotationangles, '')
        self.assertEqual(theargs.mpiexec, 'mpiexec')
        self.assertEqual(theargs.cores, None)
        self.assertEqual(theargs.etspecbin, '')


    def test_main(self):
        try:
            create_tiltseries.main(['prog', 'input', 'output'])
            self.fail('Expected OSError')
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(unittest.main())
