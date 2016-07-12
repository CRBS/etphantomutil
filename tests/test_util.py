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
import shutil
import os
import stat

from etphantomutil import util


class TestEtphantomutil(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_run_external_command_command_not_set(self):
        ecode, out, err = util.run_external_command(None)
        self.assertEqual(ecode, 255)
        self.assertEqual(out, '')
        self.assertEqual(err, 'Command must be set')

    def test_run_external_command_cmd_does_not_exist(self):
        temp_dir = tempfile.mkdtemp()
        try:
            noexist = os.path.join(temp_dir, 'noexist')
            ecode, out, err = util.run_external_command(noexist)
            self.assertEqual(ecode, 255)
            self.assertEqual(out, '')
            self.assertEqual(err, 'Caught exception trying run command: '
                                  '[Errno 2] No such file or directory')

        finally:
            shutil.rmtree(temp_dir)

    def test_run_external_command_success_with_output(self):
        temp_dir = tempfile.mkdtemp()
        try:
            script = os.path.join(temp_dir, 'yo.py')

            # create a small python script that outputs args passed
            # in to standard out, writes error to standard error
            #  and exits with 0 exit code
            f = open(script, 'w')
            f.write('#! /usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('sys.stdout.write(sys.argv[1])\n')
            f.write('sys.stdout.write(sys.argv[2])\n')
            f.write('sys.stderr.write("error")\n')
            f.write('sys.exit(0)\n')
            f.flush()
            f.close()
            os.chmod(script, stat.S_IRWXU)

            ecode, out, err = util.run_external_command(script + ' hi how')

            self.assertEqual(err, 'error')
            self.assertEqual(out, 'hihow')
            self.assertEqual(ecode, 0)

        finally:
            shutil.rmtree(temp_dir)

    def test_run_external_command_fail_with_output(self):
        temp_dir = tempfile.mkdtemp()
        try:
            script = os.path.join(temp_dir, 'yo.py')

            # create a small python script that outputs args passed
            # in to standard out, writes error to standard error
            #  and exits with 0 exit code
            f = open(script, 'w')
            f.write('#! /usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('sys.stdout.write(sys.argv[1])\n')
            f.write('sys.stdout.write(sys.argv[2])\n')
            f.write('sys.stderr.write("2error")\n')
            f.write('sys.exit(2)\n')
            f.flush()
            f.close()
            os.chmod(script, stat.S_IRWXU)

            ecode, out, err = util.run_external_command(script + ' hi how')

            self.assertEqual(err, '2error')
            self.assertEqual(out, 'hihow')
            self.assertEqual(ecode, 2)

        finally:
            shutil.rmtree(temp_dir)

    def test_run_mpiexec_command_with_command_not_set(self):
        ecode, out, err = util.run_mpiexec_command(None, None, None)
        self.assertEqual(ecode, 255)
        self.assertEqual(out, '')
        self.assertEqual(err, 'Command must be set')

    def test_run_mpiexec_command_with_mpiexec_not_set(self):
        ecode, out, err = util.run_mpiexec_command('foo', None, None)
        self.assertEqual(ecode, 255)
        self.assertEqual(out, '')
        self.assertEqual(err, 'mpiexec must be set')

    def test_run_mpiexec_command_success_with_output(self):
        temp_dir = tempfile.mkdtemp()
        try:
            script = os.path.join(temp_dir, 'yo.py')

            # create a small python script that outputs args passed
            # in to standard out, writes error to standard error
            #  and exits with 0 exit code
            f = open(script, 'w')
            f.write('#! /usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('sys.stdout.write(sys.argv[1])\n')
            f.write('sys.stdout.write(sys.argv[2])\n')
            f.write('sys.stdout.write(sys.argv[3])\n')

            f.write('sys.stderr.write("error")\n')
            f.write('sys.exit(0)\n')
            f.flush()
            f.close()
            os.chmod(script, stat.S_IRWXU)

            ecode, out, err = util.run_mpiexec_command('foo', script, 5)

            self.assertEqual(err, 'error')
            self.assertEqual(out, '-np5foo')
            self.assertEqual(ecode, 0)

        finally:
            shutil.rmtree(temp_dir)

    def test_run_mpiexec_command_fail_with_cores_not_set(self):
        temp_dir = tempfile.mkdtemp()
        try:
            script = os.path.join(temp_dir, 'yo.py')

            # create a small python script that outputs args passed
            # in to standard out, writes error to standard error
            #  and exits with 0 exit code
            f = open(script, 'w')
            f.write('#! /usr/bin/env python\n\n')
            f.write('import sys\n')
            f.write('sys.stdout.write(sys.argv[1])\n')
            f.write('sys.stdout.write(sys.argv[2])\n')
            f.write('sys.stdout.write(sys.argv[3])\n')

            f.write('sys.stderr.write("error")\n')
            f.write('sys.exit(1)\n')
            f.flush()
            f.close()
            os.chmod(script, stat.S_IRWXU)

            ecode, out, err = util.run_mpiexec_command('foo', script, None)

            self.assertEqual(err, 'error')
            self.assertEqual(out, '-np1foo')
            self.assertEqual(ecode, 1)

        finally:
            shutil.rmtree(temp_dir)

    def test_get_tilt_series_label(self):
        self.assertEqual(util.get_tilt_series_label(0), 'a')
        self.assertEqual(util.get_tilt_series_label(2), 'c')
        self.assertEqual(util.get_tilt_series_label(24), 'y')
        self.assertEqual(util.get_tilt_series_label(25), 'z')
        self.assertEqual(util.get_tilt_series_label(26), 'ba')
        self.assertEqual(util.get_tilt_series_label(27), 'bb')
        self.assertEqual(util.get_tilt_series_label(51), 'bz')
        self.assertEqual(util.get_tilt_series_label(52), 'ca')
        self.assertEqual(util.get_tilt_series_label(180), 'gy')

    def test_get_evenly_distributed_rotations(self):

        rots = util.get_evenly_distributed_rotations(1)
        self.assertEqual(len(rots), 0)

        rots = util.get_evenly_distributed_rotations(2)
        self.assertEqual(len(rots), 1)
        self.assertEqual(rots[0], 90.0)

        rots = util.get_evenly_distributed_rotations(4)
        self.assertEqual(len(rots), 3)
        self.assertEqual(rots[0], 45.0)
        self.assertEqual(rots[1], 90.0)
        self.assertEqual(rots[2], 135.0)

        rots = util.get_evenly_distributed_rotations(8)
        self.assertEqual(len(rots), 7)
        self.assertEqual(rots[0], 22.5)
        self.assertEqual(rots[6], 157.5)

        rots = util.get_evenly_distributed_rotations(16)
        self.assertEqual(len(rots), 15)
        self.assertEqual(rots[0], 11.25)
        self.assertEqual(rots[14], 168.75)

        rots = util.get_evenly_distributed_rotations(180)
        self.assertEqual(len(rots), 179)
        self.assertEqual(rots[0], 1.0)
        self.assertEqual(rots[178], 179.0)

if __name__ == '__main__':
    sys.exit(unittest.main())
