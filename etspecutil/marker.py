# -*- coding: utf-8 -*-

import math
import re
import logging
import tempfile
import shutil
import os.path

logger = logging.getLogger(__name__)

from etspecutil import util


class InvalidAngleError(Exception):
    """Raised when in invalid angle is passed in
    """
    pass


class UnsetFiducialFileError(Exception):
    """Raised when attempting to write to Unset Fiducial File
    """
    pass


class UnsetMarkersListError(Exception):
    """Raised when attempting to pass None for MarkersList
    """
    pass


class MarkersList(object):
    """Represents a set of markers
    """
    def __init__(self):
        self._markers = []

    def add_marker(self, index, x, y, z):
        self._markers.append(Marker(index, x, y, z))

    def get_markers(self):
        return self._markers

    def clear_markers(self):
        del self._markers[:]

    def rotate_by_angle(self, angle, xoffset, yoffset):
        """Rotates markers by angle
        """
        if angle is None:
            raise InvalidAngleError('Angle passed cannot be None')

        if angle == 0:
            logger.warning('Angle passed in is 0 just returning')
            return

        if xoffset is None:
            xoff = 0
        else:
            xoff = xoffset

        if yoffset is None:
            yoff = 0
        else:
            yoff = yoffset

        theta = 2 * math.pi * angle / 360
        logger.debug('angle = ' + str(angle) + ' theta = ' + str(theta) +
                     'xoffset = ' + str(xoff) + 'yoffset = ' + str(yoff))

        for m in self._markers:
            m.rotate_by_theta(theta, xoff, yoff)

    def shift_markers(self, xshift, yshift, zshift):
        """Shifts each Marker by values in xshift and yshift
        """
        for m in self._markers:
            m.shift_marker(xshift, yshift, zshift)

    def write_markers_to_file(self, file):
        """Writes markers to text file
        """
        f = open(file, 'w')
        for m in self._markers:
            f.write(m.get_3dmarker_format() + '\n')
        f.flush()
        f.close()


class Marker(object):
    """Represents a marker
    """
    def __init__(self, index, x, y, z):
        self._index = index
        self._x = x
        self._y = y
        self._z = z

    def get_index(self):
        return self._index

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def rotate_by_theta(self, theta, xoffset, yoffset):
        """Rotates marker by theta passed in

           Performs the following operation updating
           x with x' and y with y'
           x' = x*cos(theta)+y*-sin(theta)
           y' = x*sin(theta)+y*cos(theta)
        """
        newX = ((self._x - xoffset) *
                math.cos(theta) + (self._y - yoffset) * -math.sin(theta))
        newY = ((self._x - xoffset) *
                math.sin(theta) + (self._y - yoffset) * math.cos(theta))

        self._x = newX + xoffset
        self._y = newY + yoffset

    def shift_marker(self, xshift, yshift, zshift):
        """Shifts this marker by adding values passed in
           :param xshift: int value in pixels to add to x
           :param yshift: int value in pixels to add to y
           :param zshift: int value to add to z
        """
        self._x += xshift
        self._y += yshift
        self._z += zshift

    def get_3dmarker_format(self):
        """Returns marker position in ascii text format
           Format is: index x y z
           with index set as a digit that is
           left padded with 6 and the other
           values left padded by 11 as a float

           :returns: string representation of marker or empty string if any
                     of the values in the marker are `None`
        """

        if self._index is None:
            return ''
        if self._x is None:
            return ''
        if self._y is None:
            return ''
        if self._z is None:
            return ''

        return '{index:>6d} {x:>11f} ' \
               '{y:>11f} {z:>11f}'.format(index=self._index, x=self._x,
                                          y=self._y,
                                          z=self._z)


class MarkersFrom3DMarkersFileFactory(object):
    """Loads Markers from 3DMarkers.txt file
    """
    def __init__(self, markersfile):
        self._markersfile = markersfile

    def get_markers_file(self):
        """Returns path to 3DMarkers.txt file
        """
        return self._markersfile

    def set_markers_file(self, markersfile):
        """Sets markers file
        """
        self._markersfile = markersfile

    def get_markerslist(self):
        """Returns Markers from 3DMarkers.txt file set in constructor
        """
        markers = MarkersList()
        pattern = re.compile('\s+')

        f = open(self._markersfile, 'r')
        for line in f:
            pline = pattern.split(line)
            if len(pline) != 6:
                logger.warning('Skipping line invalid # elements ' +
                               str(len(pline)) + ' (' + line + ')')
                continue
            markers.add_marker(int(pline[1]), float(pline[2]),
                               float(pline[3]), float(pline[4]))
        f.close()
        return markers


class MarkersFromIMODFiducialFileFactory(object):
    """Retrieves Markers from IMOD fiducial file
    """
    def __init__(self, fiducialfile):
        self._fiducialfile = fiducialfile
        self._binary = 'model2point'

    def get_fiducial_file(self):
        """Returns path to 3DMarkers.txt file
        """
        return self._fiducialfile

    def set_fiducial_file(self, fiducialfile):
        """Sets markers file
        """
        self._fiducialfile = fiducialfile

    def set_model2point_binary(self, binary):
        """Sets alternate model2point binary
        """
        self._binary = binary

    def get_markers(self):
        """Gets markers from IMOD fiducial file
        """
        markers = MarkersList()
        if self._fiducialfile is None:
            logger.warning('Fiducial file is set to None')
            return markers

        if not os.path.isfile(self._fiducialfile):
            logger.warning('Fiducial file path does not point to file')
            return markers

        try:
            temp_dir = tempfile.mkdtemp()
            outfile = os.path.join(temp_dir, 'temp.txt')
            cmd = (self._binary + ' -float -contour ' + self._fiducialfile +
                   ' ' + outfile)
            (ecode, out, err) = util.run_external_command(cmd)
            if ecode != 0:
                raise Exception('Non zero exit code when running : ' + cmd +
                                ' : ' + err)

            fac = MarkersFrom3DMarkersFileFactory(outfile)
            return fac.get_markerslist()
        finally:
            shutil.rmtree(temp_dir)


class MarkersToIMODFiducialFileWriter(object):
    """Writes Markers to IMOD Fiducial File
    """
    def __init__(self, fiducialfile):
        self._fiducialfile = fiducialfile
        self._binary = 'point2model'

    def get_fiducial_file(self):
        """Returns path to 3DMarkers.txt file
        """
        return self._fiducialfile

    def set_fiducial_file(self, fiducialfile):
        """Sets markers file
        """
        self._fiducialfile = fiducialfile

    def set_point2model_binary(self, binary):
        """Sets alternate point2model binary
        """
        self._binary = binary

    def write_markers(self, markers):
        """Writes IMOD fiducial file with data from `markers` object passed in
        :param markers: MarkersList object containing markers to write out
        :raises UnsetFiducialFileError: If fiducial file set via constructor
                is None
        :raises UnsetMarkersListError if markers passed into this method is
         None
        :raises Exception: If invocation of point2model binary has non-zero
        exit code
        """
        if self._fiducialfile is None:
            raise UnsetFiducialFileError('Fiducial File is set to None')

        if markers is None:
            raise UnsetMarkersListError('markers cannot be None')

        try:
            temp_dir = tempfile.mkdtemp()
            tmpfile = os.path.join(temp_dir, 'out.txt')
            markers.write_markers_to_file(tmpfile)
            cmd = (self._binary + ' -circle 6 ' + tmpfile + ' ' +
                   self._fiducialfile)

            (ecode, out, err) = util.run_external_command(cmd)
            if ecode != 0:
                raise Exception('Non zero exit code when running : ' + cmd +
                                ' : ' + err)

        finally:
            shutil.rmtree(temp_dir)


class CommonByIndexMarkersListFilter(object):
    """Removes Marker objects from Markers objects that don't share indexes with
       other Markers objects passed into the constructor
    """

    def __init__(self, list_of_markers):
        """Constructor"""
        indexDict = {}
        for markersobj in list_of_markers:
            indexSet = set()
            for m in markersobj.get_markers():
                indexSet.add(m.get_index())
            for i in indexSet:
                if i not in indexDict:
                    indexDict[i] = 1
                else:
                    indexDict[i] += 1

        self._commonIndexes = []
        mlist_count = len(list_of_markers)
        for k in indexDict.keys():
            if indexDict[k] == mlist_count:
                self._commonIndexes.append(k)

    def filterMarkers(self, markers):
        """Filters out non common markers
        """
        commonM = MarkersList()
        uniqueM = MarkersList()
        for m in markers.get_markers():
            if m.get_index() in self._commonIndexes:
                commonM.add_marker(m.get_index(), m.get_x(), m.get_y(),
                                   m.get_z())
            else:
                uniqueM.add_marker(m.get_index(), m.get_x(), m.get_y(),
                                   m.get_z())
        return commonM, uniqueM
