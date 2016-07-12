# -*- coding: utf-8 -*-

import subprocess
import logging
import shlex
import string
import math
logger = logging.getLogger(__name__)


def run_external_command(cmd_to_run):
    """Runs command via external process
       :returns: tuple (exitcode, stdout, stderr)
    """

    if cmd_to_run is None:
        return 255, '', 'Command must be set'

    logger.info("Running command " + cmd_to_run)
    try:
        p = subprocess.Popen(shlex.split(cmd_to_run),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except Exception as e:
            logger.exception("Error caught exception")
            return (255, '', 'Caught exception trying run command: ' +
                    str(e))

    out, err = p.communicate()
    return p.returncode, out, err


def run_mpiexec_command(cmd_to_run, mpiexec, numcores):
    """Runs mpiexec command
    """
    if cmd_to_run is None:
        return 255, '', 'Command must be set'

    if mpiexec is None:
        return 255, '', 'mpiexec must be set'

    if numcores is None:
        core_count = 1
    else:
        core_count = numcores

    cmd = (mpiexec + ' -np ' + str(core_count) + ' ' + cmd_to_run)
    return run_external_command(cmd)


def get_tilt_series_label(tiltnumber):
    """Generates a tilt series label using the alphabet as a base 26 number system
       For example 0 would = a 25 = z 26 = ba 27 = bb (there is no aa cause a=0)
       :returns: tiltseries label by converting tiltnumber to base 26
    """
    base = 26
    convertedval = ''
    num = int(tiltnumber)
    while num >= base:
        nextchar = num % base
        convertedval = string.ascii_lowercase[nextchar] + convertedval
        num = int(num / base)

    convertedval = string.ascii_lowercase[num] + convertedval
    return convertedval

def get_evenly_distributed_rotations(num_rotations):

    rot_list = []

    degree_delta = 180 / float(num_rotations)
    cur_rot = degree_delta
    while cur_rot < 180:
        rot_list.append(cur_rot)
        cur_rot += degree_delta
    return rot_list

