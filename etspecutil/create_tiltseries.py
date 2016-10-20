#! /usr/bin/env python

import sys
import argparse
import logging
import multiprocessing

import etspecutil
from etspecutil.tiltseries import TiltSeriesCreator

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(name)s %(message)s"


class Parameters(object):
    """Holds command line arguments
    """
    pass


def _setup_logging(theargs):
    """Sets up logging for this application
    """
    theargs.logformat = LOG_FORMAT
    theargs.numericloglevel = logging.NOTSET
    if theargs.loglevel == 'DEBUG':
        theargs.numericloglevel = logging.DEBUG
    if theargs.loglevel == 'INFO':
        theargs.numericloglevel = logging.INFO
    if theargs.loglevel == 'WARNING':
        theargs.numericloglevel = logging.WARNING
    if theargs.loglevel == 'ERROR':
        theargs.numericloglevel = logging.ERROR
    if theargs.loglevel == 'CRITICAL':
        theargs.numericloglevel = logging.CRITICAL

    logger.setLevel(theargs.numericloglevel)
    logging.basicConfig(format=theargs.logformat)
    logging.getLogger('etspecutil.marker').setLevel(theargs.numericloglevel)
    logging.getLogger('etspecutil.util').setLevel(theargs.numericloglevel)
    logging.getLogger('etspecutil.tiltseries').\
        setLevel(theargs.numericloglevel)


def create_tiltseries(theargs):
    """Rotates 3DMarkers.txt file
    """
    logger.info('Creating tilt series')
    if theargs.cores is None:
        try:
            cpucount = multiprocessing.cpu_count()
        except NotImplementedError:
            logger.exception('Unable to obtain cpu count from '
                             'multiprocessing.cpu_count() defaulting to 1')
            cpucount = 1
        theargs.cores = cpucount

    logger.debug('Cores to use set to ' + str(theargs.cores))
    ts = TiltSeriesCreator(theargs)
    ts.initialize()
    ts.prepare_mrc_for_tiltseries_generation()
    ts.create_tiltseries()


def _parse_arguments(desc, args):
    """Parses command line arguments
    """
    pargs = Parameters()
    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument("inputmrcfile",
                        help='Input MRC file')
    parser.add_argument("outputdirectory",
                        help='Output directory')
    parser.add_argument("--begintilt", default=-60, type=float,
                        help='Starting tilt angle (default -60)')
    parser.add_argument("--endtilt", default=60, type=float,
                        help='Ending tilt angle (default 60)')
    parser.add_argument("--tiltshift", default=2, type=float,
                        help='Degrees between each tilt angle (default 2)')
    parser.add_argument("--nummarkers", default=20, type=float,
                        help='Number of markers aka particles to generate '
                             '(default 20)')
    parser.add_argument("--bottommarkersize", default=7, type=int,
                        help='Size of bottom markers '
                             '(default 7)')
    parser.add_argument("--topmarkersize", default=9, type=int,
                        help='Size of bottom markers '
                             '(default 9)')
    parser.add_argument("--markernoise", default=0, type=float,
                        help='Marker noise '
                             '(default 0)')
    parser.add_argument("--aparam", default=0.2, type=float,
                        help='Marker parameter named a.  No idea what it is '
                             '(default 0.2)')
    parser.add_argument("--markera", default=0.98, type=float,
                        help='Marker A parameter.  Also no idea what it is '
                             '(default 0.98)')
    parser.add_argument("--shrinkage", default=0.0005, type=float,
                        help='Shrinkage parameter in Projection section '
                             '(default 0.0005)')
    parser.add_argument("--projmaxangle", default=0.0004, type=float,
                        help='Max angle parameter in Projection section '
                             '(default 0.0004)')
    parser.add_argument("--numrotations", default='',
                        help="Used as an easier alternate"
                             "for --rotationangles flag, lets"
                             "one specify number of tilts"
                             "and the code generates optimal"
                             "angles")
    parser.add_argument("--rotationangles", default='',
                        help='Comma delimited list of rotation angles'
                             'each one will generate a tilt series.'
                             'Note: 0 rotation is always generated,'
                             'even if not in list')
    parser.add_argument("--mpiexec", default='mpiexec',
                        help='path to mpiexec binary (default mpiexec)')
    parser.add_argument("--cores",
                        help='Sets number of processing cores to use'
                             'for processing.  (default is number'
                             'of cores on machine or 1 if unable'
                             'to determine core count)')
    parser.add_argument("--etspecbin", default='',
                        help='Sets directory where ETspec/ETPhantom binaries '
                             'reside'
                             '(default empty string)')
    parser.add_argument("--log", dest="loglevel", default='WARNING',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL'],
                        help="Sets the logging level (default WARNING)")
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + etspecutil.__version__))

    return parser.parse_args(args, namespace=pargs)


def main(arglist):
    """Main entry point of script to create tilt series
    :param arglist: Should be set to sys.argv by caller
    """

    desc = """
              Wrapper application that creates simulated electron tomography
              tilt series using from SBEM MRC using ETspec
           """

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = etspecutil.__version__
    _setup_logging(theargs)

    create_tiltseries(theargs)

if __name__ == '__main__':
    main(sys.argv)
