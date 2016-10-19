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
import stat
import shutil

from etspecutil.marker import UnsetMarkersListError
from etspecutil.marker import UnsetFiducialFileError
from etspecutil.marker import MarkersToIMODFiducialFileWriter
from etspecutil.marker import MarkersList


class TestMarkersToIMODFiducialFileWriter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_set_fiducial_file(self):
        mwriter = MarkersToIMODFiducialFileWriter(None)
        self.assertEqual(mwriter.get_fiducial_file(), None)
        mwriter.set_fiducial_file('foo')
        self.assertEqual(mwriter.get_fiducial_file(), 'foo')

        mwriter = MarkersToIMODFiducialFileWriter('yo')
        self.assertEqual(mwriter.get_fiducial_file(), 'yo')
        mwriter.set_fiducial_file('foo')
        self.assertEqual(mwriter.get_fiducial_file(), 'foo')


    def test_write_markers_no_fiducial_file(self):

        mwriter = MarkersToIMODFiducialFileWriter(None)
        mlist = MarkersList()
        mlist.add_marker(1, 4, 5, 6)
        try:
            mwriter.write_markers(mlist)
            self.fail('Expected UnsetFiducialFileError')
        except UnsetFiducialFileError as e:
            self.assertEqual(str(e), 'Fiducial File is set to None')

    def test_write_markers_none_passed_in_for_markers(self):

        mwriter = MarkersToIMODFiducialFileWriter('foo')
        try:
            mwriter.write_markers(None)
            self.fail('Expected UnsetMarkersListError')
        except UnsetMarkersListError as e:
            self.assertEqual(str(e), 'markers cannot be None')

    def test_write_markers_command_fails(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mwriter = MarkersToIMODFiducialFileWriter('foo')
            mwriter.set_point2model_binary('false')
            try:
                mlist = MarkersList()
                mwriter.write_markers(mlist)
                self.fail('Expected exception')
            except Exception as e:
                self.assertTrue(str(e).startswith('Non zero exit code when '
                                                  'running : false '
                                                  '-circle 6 '))
        finally:
            shutil.rmtree(temp_dir)

    def test_write_markers_success(self):
        temp_dir = tempfile.mkdtemp()
        try:
            fid_file = os.path.join(temp_dir, 'foo')
            mwriter = MarkersToIMODFiducialFileWriter(fid_file)

            fakepoint2model = os.path.join(temp_dir, 'model2point.py')

            f = open(fakepoint2model, 'w')
            f.write('#!/usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('f = open(sys.argv[3], "r")\n')
            f.write('data = f.read()\n')
            f.write('f.close()\n')
            f.write('f = open(sys.argv[4], "w")\n')
            f.write('f.write(data)\n')
            f.write('f.close()\n')
            f.flush()
            f.close()
            os.chmod(fakepoint2model, stat.S_IRWXU)

            mwriter.set_point2model_binary(fakepoint2model)
            mlist = MarkersList()
            mlist.add_marker(1, 4, 5, 6)
            mwriter.write_markers(mlist)

            f = open(fid_file, 'r')
            data = f.read()
            self.assertEqual(data, '     1    4.000000    5.000000    '
                                   '6.000000\n')
            f.close()

        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(unittest.main())
