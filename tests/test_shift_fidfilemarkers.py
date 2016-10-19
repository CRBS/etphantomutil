#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_create_tiltseries
----------------------------------

Tests for `create_tiltseries` module.
"""

import sys
import unittest
import logging

from etspecutil import shift_fidfilemarkers
from etspecutil.rotate_3dmarkers import Parameters


class TestShiftFidFileMarkers(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        theargs = Parameters()
        theargs.loglevel = 'DEBUG'
        shift_fidfilemarkers._setup_logging(theargs)
        self.assertEqual(shift_fidfilemarkers.logger.getEffectiveLevel(),
                         logging.DEBUG)

        theargs.loglevel = 'INFO'
        shift_fidfilemarkers._setup_logging(theargs)
        self.assertEqual(shift_fidfilemarkers.logger.getEffectiveLevel(),
                         logging.INFO)

        theargs.loglevel = 'WARNING'
        shift_fidfilemarkers._setup_logging(theargs)
        self.assertEqual(shift_fidfilemarkers.logger.getEffectiveLevel(),
                         logging.WARNING)

        theargs.loglevel = 'ERROR'
        shift_fidfilemarkers._setup_logging(theargs)
        self.assertEqual(shift_fidfilemarkers.logger.getEffectiveLevel(),
                         logging.ERROR)

        theargs.loglevel = 'CRITICAL'
        shift_fidfilemarkers._setup_logging(theargs)
        self.assertEqual(shift_fidfilemarkers.logger.getEffectiveLevel(),
                         logging.CRITICAL)

    def test_parse_arguments(self):
        theargs = shift_fidfilemarkers._parse_arguments('hi', ['inputmrc',
                                                            'outdir'])
        self.assertEqual(theargs.inputfidfile, 'inputmrc')
        self.assertEqual(theargs.outputfidfile, 'outdir')
        self.assertEqual(theargs.xshift, 360)
        self.assertEqual(theargs.yshift, 360)
        self.assertEqual(theargs.loglevel, 'WARNING')

        alist = ['inputmrc', 'outdir', '--xshift', '10', '--yshift', '20',
                 '--log', 'DEBUG']
        theargs = shift_fidfilemarkers._parse_arguments('hi', alist)
        self.assertEqual(theargs.inputfidfile, 'inputmrc')
        self.assertEqual(theargs.outputfidfile, 'outdir')
        self.assertEqual(theargs.xshift, 10)
        self.assertEqual(theargs.yshift, 20)
        self.assertEqual(theargs.loglevel, 'DEBUG')

    def test_main(self):
        try:
            shift_fidfilemarkers.main(['prog', 'input', 'output'])
            self.fail('Expected OSError')
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(unittest.main())
