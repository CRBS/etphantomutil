#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_etphantomutil
----------------------------------

Tests for `etphantomutil` module.
"""


import sys
import unittest
import os.path
import tempfile
import math
import shutil

from etphantomutil.marker import Marker
from etphantomutil.marker import MarkersList

from etphantomutil.marker import MarkersFrom3DMarkersFileFactory
from etphantomutil.marker import InvalidAngleError
from etphantomutil.marker import CommonByIndexMarkersListFilter


class TestEtphantomutil(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_markers_add_get_clear(self):
        markers = MarkersList()
        self.assertEqual(len(markers.get_markers()), 0)
        markers.add_marker(1, 2, 3, 4)
        self.assertEqual(len(markers.get_markers()), 1)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 2)
        self.assertEqual(m.get_y(), 3)
        self.assertEqual(m.get_z(), 4)

        markers.add_marker(2, 3, 4, 5)
        self.assertEqual(len(markers.get_markers()), 2)
        m = markers.get_markers()[1]
        self.assertEqual(m.get_index(), 2)
        self.assertEqual(m.get_x(), 3)
        self.assertEqual(m.get_y(), 4)
        self.assertEqual(m.get_z(), 5)

        markers.clear_markers()
        self.assertEqual(len(markers.get_markers()), 0)

    def test_markers_shift(self):
        markers = MarkersList()
        markers.shift_markers(10, 20, 30)
        self.assertEqual(len(markers.get_markers()), 0)
        markers.add_marker(1, 2, 3, 4)
        markers.shift_markers(10, 20, 30)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 12)
        self.assertEqual(m.get_y(), 23)
        self.assertEqual(m.get_z(), 34)

        markers.add_marker(2, 3, 4, 5)
        markers.shift_markers(10, 20, 30)

        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 22)
        self.assertEqual(m.get_y(), 43)
        self.assertEqual(m.get_z(), 64)

        m = markers.get_markers()[1]
        self.assertEqual(m.get_index(), 2)
        self.assertEqual(m.get_x(), 13)
        self.assertEqual(m.get_y(), 24)
        self.assertEqual(m.get_z(), 35)

        markers.shift_markers(0, 0, 0)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 22)
        self.assertEqual(m.get_y(), 43)
        self.assertEqual(m.get_z(), 64)

        m = markers.get_markers()[1]
        self.assertEqual(m.get_index(), 2)
        self.assertEqual(m.get_x(), 13)
        self.assertEqual(m.get_y(), 24)
        self.assertEqual(m.get_z(), 35)

        markers.shift_markers(-10, -20, -30)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 12)
        self.assertEqual(m.get_y(), 23)
        self.assertEqual(m.get_z(), 34)

        m = markers.get_markers()[1]
        self.assertEqual(m.get_index(), 2)
        self.assertEqual(m.get_x(), 3)
        self.assertEqual(m.get_y(), 4)
        self.assertEqual(m.get_z(), 5)

    def test_markers_rotate_by_angle_none_angle(self):
        markers = MarkersList()
        try:
            markers.rotate_by_angle(None, None, None)
            self.fail('Expected InvalidAngleError')
        except InvalidAngleError:
            pass

    def test_markers_rotate_by_angle_none_offset(self):
        markers = MarkersList()
        markers.add_marker(1, 1, 0, 2)
        markers.rotate_by_angle(90, None, None)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertTrue(m.get_x() < 0.00001)
        self.assertEqual(m.get_y(), 1)
        self.assertEqual(m.get_z(), 2)

    def test_markers_rotate_by_angle_zero_offset(self):
        markers = MarkersList()

        markers.add_marker(1, 1, 0, 2)
        markers.rotate_by_angle(90, 0, 0)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertTrue(m.get_x() < 0.00001)
        self.assertEqual(m.get_y(), 1)
        self.assertEqual(m.get_z(), 2)

        # this is does nothing
        markers.rotate_by_angle(0, 0, 0)

        markers.add_marker(2, 1, 0, 3)
        markers.rotate_by_angle(90, 0, 0)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertTrue(m.get_x() < 0.00001)
        self.assertTrue(m.get_y() < 0.00001)
        self.assertEqual(m.get_z(), 2)

        m = markers.get_markers()[1]
        self.assertEqual(m.get_index(), 2)
        self.assertTrue(m.get_x() < 0.00001)
        self.assertEqual(m.get_y(), 1)
        self.assertEqual(m.get_z(), 3)

    def test_markers_rotate_by_angle_with_offset(self):
        markers = MarkersList()
        markers.add_marker(1, 1, 1, 5)
        markers.rotate_by_angle(90, 5, 5)
        m = markers.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertTrue(math.fabs(m.get_x() - 9) < 0.0001)
        self.assertTrue(math.fabs(m.get_y() - 1) < 0.0001)
        self.assertEqual(m.get_z(), 5)

    def test_markers_write_markers_to_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # invalid filename
            markers = MarkersList()
            try:
                markers.write_markers_to_file(temp_dir)
                self.fail('Expected IOError')
            except IOError:
                pass

            emptyfile = os.path.join(temp_dir, 'emptyfile')
            # empty markers object
            markers.write_markers_to_file(emptyfile)
            self.assertTrue(os.path.isfile(emptyfile))
            self.assertEqual(os.path.getsize(emptyfile), 0)

            # write 1 marker
            markers.add_marker(1, 2, 3, 4)
            one = os.path.join(temp_dir, 'one')
            markers.write_markers_to_file(one)
            self.assertTrue(os.path.isfile(one))
            f = open(one, 'r')
            line = f.readline()
            self.assertEqual(line,
                             '     1    2.000000    3.000000    4.000000\n')
            f.close()

            # write 2 markers
            markers.add_marker(2, 3, 4, 5)
            two = os.path.join(temp_dir, 'two')
            markers.write_markers_to_file(two)
            self.assertTrue(os.path.isfile(two))
            f = open(two, 'r')
            line = f.readline()
            self.assertEqual(line,
                             '     1    2.000000    3.000000    4.000000\n')
            line = f.readline()
            self.assertEqual(line,
                             '     2    3.000000    4.000000    5.000000\n')
            f.close()
        finally:
            shutil.rmtree(temp_dir)

    def test_marker_constructor(self):
        m = Marker(1, 2, 3, 4)
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 2)
        self.assertEqual(m.get_y(), 3)
        self.assertEqual(m.get_z(), 4)

    def test_marker_3dmarker_format(self):
        m = Marker(None, None, None, None)
        self.assertEqual(m.get_3dmarker_format(),
                         '')

        m = Marker(1, None, None, None)
        self.assertEqual(m.get_3dmarker_format(),
                         '')

        m = Marker(1, 1, None, None)
        self.assertEqual(m.get_3dmarker_format(),
                         '')

        m = Marker(1, 1, 1, None)
        self.assertEqual(m.get_3dmarker_format(),
                         '')

        m = Marker(1, 2, 3, 4)
        self.assertEqual(m.get_3dmarker_format(),
                         '     1    2.000000    3.000000    4.000000')

        m = Marker(10, -20, -30, -400)
        self.assertEqual(m.get_3dmarker_format(),
                         '    10  -20.000000  -30.000000 -400.000000')

        m = Marker(10, -20, -30, -4000)
        self.assertEqual(m.get_3dmarker_format(),
                         '    10  -20.000000  -30.000000 -4000.000000')

        m = Marker(1000, -20, -30, -40000)
        self.assertEqual(m.get_3dmarker_format(),
                         '  1000  -20.000000  -30.000000 -40000.000000')

    def test_marker_shift_marker(self):
        m = Marker(1, 2, 3, 4)
        m.shift_marker(0, 0, 0)
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 2)
        self.assertEqual(m.get_y(), 3)
        self.assertEqual(m.get_z(), 4)

        m.shift_marker(1, -1, 2)
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 3)
        self.assertEqual(m.get_y(), 2)
        self.assertEqual(m.get_z(), 6)

    def test_marker_rotate_by_theta(self):

        # rotate by 90
        m = Marker(1, 0, 1, 0)
        m.rotate_by_theta(2 * math.pi * 90 / 360, 0, 0)
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), -1)
        self.assertTrue(math.fabs(m.get_y()) < 0.00001)
        self.assertEqual(m.get_z(), 0)

        # rotate by -90
        m.rotate_by_theta(2 * math.pi * -90 / 360, 0, 0)
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 0)
        self.assertTrue(math.fabs(m.get_y() - 1) < 0.00001)
        self.assertEqual(m.get_z(), 0)

        # rotate by 45
        m.rotate_by_theta(2 * math.pi * 45 / 360, 0, 0)
        self.assertEqual(m.get_index(), 1)
        self.assertTrue(math.fabs(m.get_x() + 0.7071) < 0.1)
        self.assertTrue(math.fabs(m.get_y() - 0.7071) < 0.00001)
        self.assertEqual(m.get_z(), 0)

    def test_markersfrom3dmarkers_getset(self):
        fac = MarkersFrom3DMarkersFileFactory(None)
        self.assertEqual(fac.get_markers_file(), None)
        fac.set_markers_file('/foo')
        self.assertEqual(fac.get_markers_file(), '/foo')

    def test_markersfrom3dmarkers_nonefile(self):
        fac = MarkersFrom3DMarkersFileFactory(None)
        try:
            fac.get_markerslist()
            self.fail('expected exception')
        except TypeError:
            pass

    def test_markersfrom3dmarkers_nonexistantfile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            nonexistfile = os.path.join(temp_dir, 'noexist')
            fac = MarkersFrom3DMarkersFileFactory(nonexistfile)
            try:
                fac.get_markerslist()
                self.fail('Expected IOError')
            except IOError:
                pass

        finally:
            shutil.rmtree(temp_dir)

    def test_markersfrom3dmarkers_emptyfile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            emptyfile = os.path.join(temp_dir, 'empty')
            open(emptyfile, 'a').close()
            fac = MarkersFrom3DMarkersFileFactory(emptyfile)
            m = fac.get_markerslist()
            self.assertEqual(len(m.get_markers()), 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_markersfrom3dmarkers_onelinefile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mfile = os.path.join(temp_dir, '3Dmarkers.txt')
            f = open(mfile, 'w')
            f.write('     1  442.000000  633.000000   12.000000\n')
            f.flush()
            f.close()
            fac = MarkersFrom3DMarkersFileFactory(mfile)
            m = fac.get_markerslist()
            marker = m.get_markers()[0]
            self.assertEqual(marker.get_index(), 1)
            self.assertEqual(marker.get_x(), 442)
            self.assertEqual(marker.get_y(), 633)
            self.assertEqual(marker.get_z(), 12)
        finally:
            shutil.rmtree(temp_dir)

    def test_markersfrom3dmarkers_multifile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mfile = os.path.join(temp_dir, '3Dmarkers.txt')
            f = open(mfile, 'w')
            f.write('     1  442.000000  633.000000   12.000000\n')
            f.write('     2  452.000000  485.000000   12.000000\n')
            f.write('     3  498.000000  532.000000   12.000000\n')
            f.write('     4  403.000000  689.000000   12.000000\n')
            f.write('     5  505.000000  421.000000   12.000000\n')
            f.write('     6  440.000000  420.000000   12.000000\n')
            f.write('     7  670.000000  417.000000   12.000000\n')
            f.write('     8  429.000000  544.000000   12.000000\n')
            f.write('     9  532.000000  585.000000   12.000000\n')
            f.write('    10  451.000000  471.000000  100.000000\n')

            f.flush()
            f.close()
            fac = MarkersFrom3DMarkersFileFactory(mfile)
            m = fac.get_markerslist()
            self.assertEqual(len(m.get_markers()), 10)
            marker = m.get_markers()[0]
            self.assertEqual(marker.get_index(), 1)
            self.assertEqual(marker.get_x(), 442)
            self.assertEqual(marker.get_y(), 633)
            self.assertEqual(marker.get_z(), 12)
            marker = m.get_markers()[9]
            self.assertEqual(marker.get_index(), 10)
            self.assertEqual(marker.get_x(), 451)
            self.assertEqual(marker.get_y(), 471)
            self.assertEqual(marker.get_z(), 100)
        finally:
            shutil.rmtree(temp_dir)

    def test_markersfrom3dmarkers_filewithbadlines(self):
        temp_dir = tempfile.mkdtemp()
        try:
            mfile = os.path.join(temp_dir, '3Dmarkers.txt')
            f = open(mfile, 'w')
            f.write('     1  442.000000  633.000000   12.000000\n')
            f.write('     2  452.000000  485.000000\n')
            f.write('    10  451.000000  471.000000  100.000000\n')

            f.flush()
            f.close()
            fac = MarkersFrom3DMarkersFileFactory(mfile)
            m = fac.get_markerslist()
            self.assertEqual(len(m.get_markers()), 2)
            marker = m.get_markers()[0]
            self.assertEqual(marker.get_index(), 1)
            self.assertEqual(marker.get_x(), 442)
            self.assertEqual(marker.get_y(), 633)
            self.assertEqual(marker.get_z(), 12)
            marker = m.get_markers()[1]
            self.assertEqual(marker.get_index(), 10)
            self.assertEqual(marker.get_x(), 451)
            self.assertEqual(marker.get_y(), 471)
            self.assertEqual(marker.get_z(), 100)
        finally:
            shutil.rmtree(temp_dir)

    # test Common 1 markerslist
    def test_filtermarkers_one_markerlist(self):
        mlist = MarkersList()
        mlist.add_marker(1, 2, 3, 4)
        mlist.add_marker(1, 2, 3, 5)
        mlist.add_marker(1, 2, 3, 6)
        thelist = []
        thelist.append(mlist)
        filt = CommonByIndexMarkersListFilter(thelist)

        com,uni = filt.filterMarkers(mlist)

        self.assertTrue(len(uni.get_markers()) == 0)
        self.assertTrue(len(com.get_markers()) == 3)
        m = com.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 2)
        self.assertEqual(m.get_y(), 3)
        self.assertEqual(m.get_z(), 4)


    # test Common 2 markerslist identical
    def test_filtermarkers_two_identical_markerlist(self):
        mlist = MarkersList()
        mlist.add_marker(1, 2, 3, 4)
        mlist.add_marker(1, 2, 3, 5)
        mlist.add_marker(1, 2, 3, 6)
        thelist = []
        thelist.append(mlist)
        thelist.append(mlist)
        filt = CommonByIndexMarkersListFilter(thelist)

        com,uni = filt.filterMarkers(mlist)

        self.assertTrue(len(uni.get_markers()) == 0)
        self.assertTrue(len(com.get_markers()) == 3)
        m = com.get_markers()[0]
        self.assertEqual(m.get_index(), 1)
        self.assertEqual(m.get_x(), 2)
        self.assertEqual(m.get_y(), 3)
        self.assertEqual(m.get_z(), 4)

    # test Common 3 markerslist one missing in each
    def test_filtermarkers_one_markerlist(self):
        mlist1 = MarkersList()
        mlist1.add_marker(1, 2, 3, 4)
        mlist1.add_marker(1, 2, 3, 5)
        mlist1.add_marker(2, 2, 3, 6)
        mlist1.add_marker(4, 2, 3, 6)
        mlist1.add_marker(4, 2, 3, 7)

        thelist = []
        thelist.append(mlist1)

        mlist2 = MarkersList()
        mlist2.add_marker(1, 2, 3, 4)
        mlist2.add_marker(1, 2, 3, 5)
        mlist2.add_marker(3, 2, 3, 6)
        mlist2.add_marker(4, 2, 3, 6)
        mlist2.add_marker(4, 2, 3, 7)
        thelist.append(mlist2)

        mlist3 = MarkersList()
        mlist3.add_marker(1, 2, 3, 4)
        mlist3.add_marker(1, 2, 3, 5)
        mlist3.add_marker(3, 2, 3, 6)
        mlist3.add_marker(4, 2, 3, 6)
        mlist3.add_marker(5, 1, 1, 1)
        thelist.append(mlist3)

        filt = CommonByIndexMarkersListFilter(thelist)

        com,uni = filt.filterMarkers(mlist1)

        self.assertTrue(len(uni.get_markers()) == 1)
        self.assertTrue(len(com.get_markers()) == 4)

        self.assertEqual(uni.get_markers()[0].get_index(), 2)
        self.assertEqual(uni.get_markers()[0].get_z(), 6)

        com,uni = filt.filterMarkers(mlist2)

        self.assertTrue(len(uni.get_markers()) == 1)
        self.assertTrue(len(com.get_markers()) == 4)

        self.assertEqual(uni.get_markers()[0].get_index(), 3)
        self.assertEqual(uni.get_markers()[0].get_y(), 3)

        com,uni = filt.filterMarkers(mlist3)

        self.assertTrue(len(uni.get_markers()) == 2)
        self.assertTrue(len(com.get_markers()) == 3)

        self.assertEqual(uni.get_markers()[0].get_index(), 3)
        self.assertEqual(uni.get_markers()[0].get_y(), 3)
        self.assertEqual(uni.get_markers()[1].get_index(), 5)
        self.assertEqual(uni.get_markers()[1].get_y(), 1)


if __name__ == '__main__':
    sys.exit(unittest.main())
