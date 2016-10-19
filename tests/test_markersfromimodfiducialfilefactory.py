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

from etspecutil.marker import MarkersFromIMODFiducialFileFactory


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

    def test_get_markers_model2point_succeeds(self):
        temp_dir = tempfile.mkdtemp()
        try:
            fid_file = os.path.join(temp_dir, 'somefile.txt')
            open(fid_file, 'a').close()
            mfac = MarkersFromIMODFiducialFileFactory(fid_file)

            fakemodel2point = os.path.join(temp_dir, 'model2point.py')

            f = open(fakemodel2point, 'w')
            f.write('#!/usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('f = open(sys.argv[4], "w")\n')
            f.write('f.write("     1      188.52      283.08        0.00\\n")\n')
            f.write('f.write("     1      192.29      283.06        1.00\\n")\n')
            f.write('f.write("     1      196.04      283.04        2.00\\n")\n')
            f.write('f.close()\n')
            f.flush()
            f.close()
            os.chmod(fakemodel2point, stat.S_IRWXU)
            print 'XXXXXX',temp_dir
            # import time
            # time.sleep(1000)
            mfac.set_model2point_binary(fakemodel2point)

            mlist = mfac.get_markers()
            self.assertEqual(len(mlist.get_markers()), 3)
            m = mlist.get_markers()[0]
            self.assertEqual(m.get_x(), 188.52)
            m = mlist.get_markers()[1]
            self.assertEqual(m.get_x(), 192.29)
            m = mlist.get_markers()[2]
            self.assertEqual(m.get_x(), 196.04)

        finally:
            shutil.rmtree(temp_dir)



if __name__ == '__main__':
    sys.exit(unittest.main())
