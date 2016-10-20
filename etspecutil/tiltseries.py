# -*- coding: utf-8 -*-

import os.path
import logging
import re
import math
import shutil
from etspecutil import util
from etspecutil.marker import MarkersFrom3DMarkersFileFactory
from etspecutil.marker import CommonByIndexMarkersListFilter


logger = logging.getLogger(__name__)


class TiltSeriesCreator(object):
    """Creates a phantom tilt series using ETSpec
    """
    MRC_EXT = '.mrc'
    UNI_MRC_EXT = '_uni' + MRC_EXT
    EXT_MEAN_EXT = '_ext_mean' + MRC_EXT
    RAW_TLT_EXT = '.rawtlt'
    WARPZ_EXT = '_warpz_0' + MRC_EXT
    MARKERMRC_EXT = '_marker_0' + MRC_EXT
    PAR_EXT = '.par'
    PRO_EXT = '.pro'
    LOG_EXT = '.log'
    FID_EXT = '.fid'
    PREALI_EXT = '.preali'
    RESULT_DIR_NAME = 'result'
    WARPZ_DIR_NAME = 'warpz'
    MARKER_DIR_NAME = 'marker'
    PROJECTION_DIR_NAME = 'projection'
    TRACKING_DIR_NAME = 'tracking'
    TILTSERIES_DIR_NAME = 'tiltseries'
    PREPARED_DIR_NAME = 'prepared'
    THREE_D_MARKERS_TXT = '3Dmarkers.txt'
    PROJECTION = '_projection'
    PROJECTION_EXT = PROJECTION + MRC_EXT
    PROJECTION_CLIP = '_projection_clip'
    PROJECTION_CLIP_EXT = PROJECTION_CLIP + MRC_EXT
    OFFSET_ALL_TXT = 'offset_all.txt'
    TWO_D_MARKERS_ALL_TXT = '2Dmarkers_all.txt'
    TWO_D_MARKERS_ALL_FID = '2Dmarkers_all' + FID_EXT
    TWO_D_MARKERS_COMMON_TXT = '2Dmarkers_common.txt'

    def __init__(self, theargs):
        """Constructor that takes one parameter which should contain
        a whole bunch of attributes as defined below

        :param theargs: Object with the following attributes set
                        theargs.outputdirectory
                        theargs.inputmrcfile
                        theargs.begintilt
                        theargs.endtilt
                        theargs.tiltshift
                        theargs.cores
                        theargs.mpiexec
                        theargs.nummarkers
                        theargs.bottommarkersize
                        theargs.topmarkersize
                        theargs.markernoise
                        theargs.aparam
                        theargs.markera
                        theargs.shrinkage
                        theargs.projmaxangle
                        theargs.numrotations
                        theargs.rotatinoangles
                        theargs.etspecbin
        :raises AttributeError: if the above attributes are not set
        """
        self._outdir = theargs.outputdirectory
        self._workdir = os.getcwd()
        self._inputmrc = os.path.abspath(theargs.inputmrcfile)
        self._begintilt = theargs.begintilt
        self._endtilt = theargs.endtilt
        self._tiltshift = theargs.tiltshift
        self._cores = theargs.cores
        self._mpiexec = theargs.mpiexec
        self._nummarkers = theargs.nummarkers
        self._bottommarkersize = theargs.bottommarkersize
        self._topmarkersize = theargs.topmarkersize
        self._markernoise = theargs.markernoise
        self._aparam = theargs.aparam
        self._markera = theargs.markera
        self._shrinkage = theargs.shrinkage
        self._projmaxangle = theargs.projmaxangle

        self._rawrotationangles = None
        if theargs.numrotations is not '':
            logger.info('Numrotations set to: ' + theargs.numrotations)
            self._rawrotationlist = util.\
                get_evenly_distributed_rotations(int(theargs.numrotations))
        else:
            self._rawrotationangles = theargs.rotationangles

        if theargs.etspecbin == '':
            self._etspecbin = theargs.etspecbin
        else:
            self._etspecbin = os.path.abspath(theargs.etspecbin)

    def initialize(self):
        """Initializes file system
        """
        if not os.path.isdir(self._outdir):
            os.makedirs(self._outdir)
            os.chdir(self._outdir)
            self._outdir = os.getcwd()

        preparedir = os.path.join(self._outdir,
                                  TiltSeriesCreator.PREPARED_DIR_NAME)
        if not os.path.isdir(preparedir):
            os.makedirs(preparedir)

        self._inputmrcname = os.path.basename(self._inputmrc)

        self._mrcname = re.sub(TiltSeriesCreator.MRC_EXT + '$', '',
                               self._inputmrcname)
        self._unimrc = self._mrcname + TiltSeriesCreator.UNI_MRC_EXT

        self._extmeanmrc = self._mrcname + TiltSeriesCreator.EXT_MEAN_EXT

        self._rawtlt = self._mrcname + TiltSeriesCreator.RAW_TLT_EXT

        self._warpz = self._mrcname + TiltSeriesCreator.WARPZ_EXT

        self._markermrc = self._mrcname + TiltSeriesCreator.MARKERMRC_EXT

        self._projectionmrc = self._mrcname + TiltSeriesCreator.PROJECTION_EXT

        self._projectionclipmrc = (self._mrcname +
                                   TiltSeriesCreator.PROJECTION_CLIP_EXT)

        self._projectionclipfid = (self._mrcname +
                                   TiltSeriesCreator.PROJECTION_CLIP +
                                   TiltSeriesCreator.FID_EXT)

        rotations = [float(0)]

        if self._rawrotationangles is not None:
            for a in self._rawrotationangles.split(','):
                try:
                    af = float(a)
                    if af > 0:
                        if af <= 180:
                            if af not in rotations:
                                rotations.append(af)
                except ValueError:
                    logger.warning('Unable to parse angle from element ' + a)
        else:
            rotations.extend(self._rawrotationlist)

        self._rotationangles = sorted(rotations)
        logger.info('Processing ' + str(len(self._rotationangles)) +
                    ' rotations')
        for r in self._rotationangles:
            logger.info('Rotation: ' + str(r))

    def prepare_mrc_for_tiltseries_generation(self):
        """Performs initial steps needed to generate tilt series
        """
        current_working_dir = os.getcwd()
        try:
            logger.debug('Changing to ' + self._outdir + ' directory')
            os.chdir(self._outdir)
            logger.debug('Changing to ' + TiltSeriesCreator.PREPARED_DIR_NAME +
                         ' directory')
            os.chdir(TiltSeriesCreator.PREPARED_DIR_NAME)
            self._workdir = os.getcwd()
            self._preparedir = self._workdir

            # run all_255
            self._run_all_255()

            # run extend_mean
            self._run_extend_mean()

            # run rawtilt
            self._run_raw_tilt()

            # run warpz
            self._run_warpz()

            # run volume_marker
            self._run_volume_marker()

            # write the parameter file
            self._write_etspec_parameter_file()
            self._write_etspec_prepared_project_file()

        finally:
            logger.debug('Changing back to ' + current_working_dir +
                         ' directory')
            os.chdir(current_working_dir)

    def _run_all_255(self):
        """Runs all_255 command
        """
        cmd = (os.path.join(self._etspecbin, 'all_255') + ' ' +
               self._inputmrc + ' ' +
               os.path.join(self._workdir, self._unimrc))
        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      self._cores)
        if exitcode != 0:
            raise Exception('Unable to run all_255 : ' + err)

    def _run_extend_mean(self):
        """Runs exteand_mean command
        """
        cmd = (os.path.join(self._etspecbin, 'extend_mean') + ' ' +
               os.path.join(self._workdir, self._unimrc) + ' ' +
               os.path.join(self._workdir, self._extmeanmrc))
        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      self._cores)
        if exitcode != 0:
            raise Exception('Unable to run extend_mean : ' + err)

    def _run_raw_tilt(self):
        """Runs exteand_mean command
        """
        cmd = (os.path.join(self._etspecbin, 'rawtlt') + ' ' +
               str(self._begintilt) + ' ' + str(self._tiltshift) + ' ' +
               str(self._endtilt) + ' ' +
               os.path.join(self._workdir, self._rawtlt))

        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      1)
        if exitcode != 0:
            raise Exception('Unable to run rawtlt : ' + err)

    def _get_warpz_dir(self):
        """Gets warpz dir
        """
        return os.path.join(self._workdir,
                            TiltSeriesCreator.WARPZ_DIR_NAME)

    def _get_marker_dir(self):
        """Gets marker dir
        """
        return os.path.join(self._workdir,
                            TiltSeriesCreator.MARKER_DIR_NAME)

    def _get_projection_dir(self):
        """Gets projection directory
        """
        return os.path.join(self._workdir,
                            TiltSeriesCreator.PROJECTION_DIR_NAME)

    def _get_tracking_dir(self):
        """Gets tracking directory
        """
        return os.path.join(self._workdir,
                            TiltSeriesCreator.TRACKING_DIR_NAME)

    def _get_result_dir(self):
        return os.path.join(self._outdir,
                            TiltSeriesCreator.RESULT_DIR_NAME)

    def _run_warpz(self):
        """Runs exteand_mean command
        """
        warpzdir = self._get_warpz_dir()
        if not os.path.isdir(warpzdir):
            os.makedirs(warpzdir)

        cmd = (os.path.join(self._etspecbin, 'warpZ_inter_del') + ' ' +
               os.path.join(self._workdir, self._extmeanmrc) + ' ' +
               os.path.join(self._workdir, self._extmeanmrc) + ' ' +
               os.path.join(warpzdir, self._warpz) + ' ' +
               str(self._get_number_of_tilts()) + ' 0 0 0 0')

        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      self._cores)
        if exitcode != 0:
            raise Exception('Unable to run warpZ_inter_del : ' + err)

    def _run_volume_marker(self):
        """Runs exteand_mean command
        """
        markerdir = self._get_marker_dir()
        if not os.path.isdir(markerdir):
            os.makedirs(markerdir)

        warpzdir = self._get_warpz_dir()

        cmd = (os.path.join(self._etspecbin, 'volume_marker') + ' ' +
               os.path.join(self._workdir, self._extmeanmrc) + ' ' +
               os.path.join(warpzdir, self._warpz) + ' ' +
               os.path.join(markerdir, self._markermrc) + ' ' +
               str(self._nummarkers) + ' ' +
               str(self._bottommarkersize) + ' ' +
               str(self._topmarkersize) + ' ' +
               str(self._markernoise) + ' ' +
               str(self._get_number_of_tilts()) + ' 0 0 0 0 0 ' +
               str(self._markera) + ' ' +
               str(self._aparam))

        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      self._cores)
        if exitcode != 0:
            raise Exception('Unable to run rawtlt : ' + err)

    def _get_number_of_tilts(self):
        """Gets number of tilts
        """
        if self._begintilt > self._endtilt:
            largest_tilt = self._begintilt
            smallest_tilt = self._endtilt
        else:
            largest_tilt = self._endtilt
            smallest_tilt = self._begintilt
        return int(math.ceil((largest_tilt - smallest_tilt) / self._tiltshift))

    def create_tiltseries(self):
        """Using output from `generate_basetiltseries` creates tiltseries

           The generated tilt series are compatible with Txbr 3.0.0
        """
        dirlist = []
        for rotation in self._rotationangles:
            logger.info('Creating tilt series for rotation: ' + str(rotation))
            rotationdir = os.path.join(self._outdir, str(rotation) + '_' +
                                       TiltSeriesCreator.TILTSERIES_DIR_NAME)
            if os.path.isdir(rotationdir):
                logger.info('Skipping rotation ' + str(rotation) +
                            ' since directory exists')
                continue

            logger.info('Copying prepared dir to ' + rotationdir)
            shutil.copytree(self._preparedir, rotationdir)
            os.chdir(rotationdir)
            # do processing here
            self._generate_tilt_series(rotation, rotationdir)
            dirlist.append(rotationdir)
            os.chdir(self._outdir)

        self._generate_common_marker_files(dirlist)

    def _get_common_markers_filter(self, dirlist):
        mlist = []
        for path in dirlist:
            logger.debug('Loading markers from ' + path)
            self._workdir = path
            two_d_txt = os.path.join(self._get_tracking_dir(),
                                     TiltSeriesCreator.TWO_D_MARKERS_ALL_TXT)
            mfac = MarkersFrom3DMarkersFileFactory(two_d_txt)
            markers = mfac.get_markerslist()
            mlist.append(markers)

        return CommonByIndexMarkersListFilter(mlist)

    def _generate_common_marker_files(self, dirlist):
        """For each rotation eliminate missing tracks and write out
           a new marker file and .fid file for each rotationdir
        """
        filt = self._get_common_markers_filter(dirlist)

        for path in dirlist:
            logger.debug('Saving common markers for ' + path)
            self._workdir = path
            two_d_txt = os.path.join(self._get_tracking_dir(),
                                     TiltSeriesCreator.TWO_D_MARKERS_ALL_TXT)
            mfac = MarkersFrom3DMarkersFileFactory(two_d_txt)
            markers = mfac.get_markerslist()
            com, uni = filt.filterMarkers(markers)
            for m in uni.get_markers():
                logger.debug('Unique marker ommitted: ' +
                             m.get_3dmarker_format())

            com_txt = os.path.join(self._get_tracking_dir(),
                                   TiltSeriesCreator.TWO_D_MARKERS_COMMON_TXT)
            com.write_markers_to_file(com_txt)
            self._run_point2model_common()
            self._run_shift_fidfilemarkers_common()

        self._put_all_tilts_into_result_dir(dirlist)

    def _put_all_tilts_into_result_dir(self, dirlist):

        resultdir = self._get_result_dir()
        if not os.path.isdir(resultdir):
            os.makedirs(resultdir)

        counter = 0
        for path in dirlist:
            tiltname = util.get_tilt_series_label(counter)
            # copy clip mrc file
            shutil.copy(os.path.join(path, self._projectionclipmrc),
                        os.path.join(resultdir, self._mrcname + tiltname +
                                     TiltSeriesCreator.PREALI_EXT))

            # copy clip fid file
            shutil.copy(os.path.join(path, self._projectionclipfid),
                        os.path.join(resultdir, self._mrcname +
                                     tiltname +
                                     TiltSeriesCreator.FID_EXT))

            # copy rawtilt if it exists
            rawtlt = os.path.join(path, self._rawtlt)
            if os.path.isfile(rawtlt):
                destrawtlt = os.path.join(resultdir, self._mrcname + tiltname +
                                          TiltSeriesCreator.RAW_TLT_EXT)
                shutil.copy(rawtlt, destrawtlt)
            else:
                if destrawtlt is not None:

                    shutil.copy(destrawtlt,
                                os.path.join(resultdir,
                                             self._mrcname + tiltname +
                                             TiltSeriesCreator.RAW_TLT_EXT))
            counter += 1

    def _generate_tilt_series(self, rotation, rotationdir):
        """Generates tilt series for rotation passed in
        """
        self._workdir = rotationdir

        # rotate marker mrc file and 3Dmarkers.txt file
        if math.fabs(rotation) > 0.001:
            self._run_rotatevol(rotation)
            self._run_rotate_3dmarkers(rotation)

        self._run_project_all()
        self._run_clip_projection_mrc()
        self._run_volume_marker_position_all()
        self._run_point2model()

    def _run_rotatevol(self, rotation):
        """Rotates mrc volume
        """
        markermrc = os.path.join(self._get_marker_dir(), self._markermrc)
        tmp_mrc = os.path.join(self._get_marker_dir(), 'tmp.mrc')
        cmd = ('rotatevol -angles ' + str(rotation) + ',0,0 ' +
               markermrc + ' ' + tmp_mrc)

        exitcode, out, err = util.run_external_command(cmd)
        if exitcode != 0:
            raise Exception('Unable to run rotatevol : ' + err)

        shutil.move(tmp_mrc, markermrc)

    def _run_rotate_3dmarkers(self, rotation):
        """ Rotates 3Dmarkers.txt file
        :param rotation:
        :return:
        """
        (x, y, z) = self._get_mrc_marker_image_dimensions()
        three_d_markers_file = os.path.join(self._get_marker_dir(),
                                            TiltSeriesCreator.
                                            THREE_D_MARKERS_TXT)
        cmd = ('rotate_3dmarkers.py --angle ' + str(rotation) +
               ' --width ' + str(x) + ' --height ' + str(y) + ' ' +
               three_d_markers_file)

        exitcode, out, err = util.run_external_command(cmd,)
        if exitcode != 0:
            raise Exception('Unable to run rotate_3dmarkers.py : ' + err)

    def _run_project_all(self):
        """Runs project_all
        """
        projectiondir = self._get_projection_dir()
        if not os.path.isdir(projectiondir):
            os.makedirs(projectiondir)

        cmd = (os.path.join(self._etspecbin, 'project_all') + ' ' +
               os.path.join(self._get_marker_dir(), self._markermrc) + ' ' +
               os.path.join(self._workdir, self._projectionmrc) + ' ' +
               str(self._begintilt) + ' ' +
               str(self._tiltshift) + ' ' +
               str(self._endtilt) + ' ' +
               str(self._shrinkage) + ' ' +
               str(self._projmaxangle) + ' 0 0 0 0')

        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      self._cores)
        if exitcode != 0:
            raise Exception('Unable to run project_all : ' + err)

    def _run_clip_projection_mrc(self):
        """Runs clip resize to get a clipped mrc file
        """
        (x, y, z) = self._get_mrc_marker_image_dimensions()
        cmd = ('clip resize -ox ' + str(int(int(x)/3)) + ' -oy ' +
               str(int(int(y)/3)) + ' ' +
               os.path.join(self._workdir, self._projectionmrc) + ' ' +
               os.path.join(self._workdir, self._projectionclipmrc))

        exitcode, out, err = util.run_external_command(cmd)
        if exitcode != 0:
            raise Exception('Unable to run clip : ' + err)

    def _run_volume_marker_position_all(self):
        """Runs volume_marker_position_all
        """
        trackingdir = self._get_tracking_dir()
        if not os.path.isdir(trackingdir):
            os.makedirs(trackingdir)

        cmd = (os.path.join(self._etspecbin, 'volume_marker_position_all') +
               ' ' +
               os.path.join(self._get_marker_dir(), self._markermrc) + ' ' +
               os.path.join(self._get_marker_dir(),
                            TiltSeriesCreator.THREE_D_MARKERS_TXT) + ' ' +
               os.path.join(self._get_projection_dir(),
                            TiltSeriesCreator.OFFSET_ALL_TXT) + ' ' +
               str(self._nummarkers) + ' ' +
               str(self._begintilt) + ' ' +
               str(self._tiltshift) + ' ' +
               str(self._endtilt) + ' ' +
               str(self._shrinkage) + ' ' +
               str(self._projmaxangle) + ' 0 0 0 0')

        exitcode, out, err = util.run_mpiexec_command(cmd, self._mpiexec,
                                                      1)
        if exitcode != 0:
            raise Exception('Unable to run volume_marker_position_all : ' +
                            err)

    def _run_point2model(self):
        """runs point2model for fid file
        """
        two_d_fid = os.path.join(self._workdir,
                                 TiltSeriesCreator.TWO_D_MARKERS_ALL_FID)
        cmd = ('point2model -circle 6 ' +
               os.path.join(self._get_tracking_dir(),
                            TiltSeriesCreator.TWO_D_MARKERS_ALL_TXT) + ' ' +
               two_d_fid)

        exitcode, out, err = util.run_external_command(cmd)
        if exitcode != 0:
            raise Exception('Unable to run point2model : ' +
                            err)

    def _run_point2model_common(self):
        """runs point2model for fid file
        """
        common_fid = os.path.join(self._workdir,
                                  self._mrcname +
                                  TiltSeriesCreator.PROJECTION_CLIP +
                                  TiltSeriesCreator.FID_EXT)

        cmd = ('point2model -circle 6 ' +
               os.path.join(self._get_tracking_dir(),
                            TiltSeriesCreator.TWO_D_MARKERS_COMMON_TXT) + ' ' +
               common_fid)

        exitcode, out, err = util.run_external_command(cmd)
        if exitcode != 0:
            raise Exception('Unable to run point2model : ' +
                            err)

    def _run_shift_fidfilemarkers_common(self):
        """Runs shift_fidfilemarkers to shift fid file for non clipped
           projection
        """
        common_fid = os.path.join(self._workdir,
                                  self._mrcname +
                                  TiltSeriesCreator.PROJECTION_CLIP +
                                  TiltSeriesCreator.FID_EXT)

        (x, y, z) = self._get_mrc_marker_image_dimensions()
        cmd = ('shift_fidfilemarkers.py --xshift ' + str(int(int(x)/3)) +
               ' --yshift ' +
               str(int(int(y)/3)) + ' ' +
               common_fid + ' ' +
               os.path.join(self._workdir, self._mrcname +
                            TiltSeriesCreator.PROJECTION +
                            TiltSeriesCreator.FID_EXT))

        exitcode, out, err = util.run_external_command(cmd)
        if exitcode != 0:
            raise Exception('Unable to run shif_fidfilemarkers.py : ' + err)

    def _get_mrc_marker_image_dimensions(self):
        """Gets dimensions of marker mrc file
        :returns tuple: x, y, z
        """
        markermrc = os.path.join(self._get_marker_dir(), self._markermrc)
        cmd = ('header -s ' + markermrc)
        exitcode, out, err = util.run_external_command(cmd,)
        if exitcode != 0:
            raise Exception('Unable to run header -s : ' + err)

        list = re.split('\s+', out)
        if len(list) != 5:
            raise Exception('Invalid output from header : ' + out)
        return list[1], list[2], list[3]

    def _write_etspec_parameter_file(self):
        """Writes etspec parameter file
        """
        f = open(os.path.join(self._workdir, self._mrcname +
                              TiltSeriesCreator.PAR_EXT), 'w')
        f.write('ANGLE_BEGIN = ' + str(self._begintilt) + '\n')
        f.write('ANGLE_INTER = ' + str(self._tiltshift) + '\n')
        f.write('ANGLE_END = ' + str(self._endtilt) + '\n')
        f.write('EXTEND_TYPE = mean\n')
        f.write('WARP_MODE = nowarp\n')
        f.write('WARPZ_SIGMA = 0\n')
        f.write('WARPZ_TAO = 0\n')
        f.write('WARPZ_ALPHA = 0\n')
        f.write('MARKER_TYPE = Gaussian\n')
        f.write('MARKER_NUMBER = ' + str(self._nummarkers) + '\n')
        f.write('MARKER_BSIZE = ' + str(self._bottommarkersize) + '\n')
        f.write('MARKER_TSIZE = ' + str(self._topmarkersize) + '\n')
        f.write('MARKER_NOISE = ' + str(self._markernoise) + '\n')
        f.write('MARKER_A = ' + str(self._markera) + '\n')
        f.write('MARKER_B = ' + str(self._aparam) + '\n')
        f.write('TWIST_SHRINKAGE = ' + str(self._shrinkage) + '\n')
        f.write('TWIST_MAXANGLE = ' + str(self._projmaxangle) + '\n')
        f.write('SHIFT_OFFSET = 0\n')
        f.write('SHIFT_ROTATEANGEL = 0\n')
        f.write('DRIFT_XSIZE = 0\n')
        f.write('DRIFT_YSIZE = 0\n')
        f.flush()
        f.close()

    def _write_etspec_prepared_project_file(self):
        """Writes etspec project file for prepared
           phase
        """
        f = open(os.path.join(self._workdir, self._mrcname +
                              TiltSeriesCreator.PRO_EXT), 'w')
        f.write('PROJECT_NAME = ' + self._mrcname + '\n')
        f.write('PRO_NAME = ' + self._mrcname + TiltSeriesCreator.PRO_EXT +
                '\n')
        f.write('MRC_DIR = ' + self._inputmrc + '\n')
        f.write('SYSLOG_FILE = ' + self._mrcname + TiltSeriesCreator.LOG_EXT +
                '\n')
        f.write('PAR_FILE = ' + self._mrcname + TiltSeriesCreator.PAR_EXT +
                '\n')
        f.write('UNI_MRC_DIR = ' + self._unimrc + '\n')
        f.write('EXTEND_MRC_DIR = ' + self._extmeanmrc + '\n')
        f.write('WARPZ_MRC_DIR = ' +
                os.path.join(TiltSeriesCreator.WARPZ_DIR_NAME,
                             self._warpz) + '\n')
        f.write('WARPMODE = nowarp\n')
        f.write('MARKER_MRC_DIR = ' +
                os.path.join(TiltSeriesCreator.MARKER_DIR_NAME,
                             self._markermrc) + '\n')
        f.write('PREPROCESS_STATE = FINISH\n')
        f.write('NORMALIZE_STATE = FINISH\n')
        f.write('UNIFORM_STATE = FINISH\n')
        f.write('WARP_STATE = FINISH\n')
        f.write('EXTEND_STATE = FINISH\n')
        f.write('WARPZ_STATE = FINISH\n')
        f.write('MARKER_STATE = FINISH\n')
        f.write('MARKERSTART_STATE = FINISH\n')
        f.flush()
        f.close()
