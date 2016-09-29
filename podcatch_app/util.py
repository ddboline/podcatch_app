#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shlex
import time
from subprocess import call, Popen, PIPE
import requests
from requests import HTTPError

HOSTNAME = os.uname()[1]
HOMEDIR = os.getenv('HOME')
POSTGRESTRING = 'postgresql://ddboline:BQGIvkKFZPejrKvX@localhost'


class PopenWrapperClass(object):
    """ context wrapper around subprocess.Popen """
    def __init__(self, command):
        """ init fn """
        self.command = command
        self.pop_ = Popen(self.command, shell=True, stdout=PIPE)

    def __iter__(self):
        return self.pop_.stdout

    def __enter__(self):
        """ enter fn """
        return self.pop_.stdout

    def __exit__(self, exc_type, exc_value, traceback):
        """ exit fn """
        if hasattr(self.pop_, '__exit__'):
            efunc = getattr(self.pop_, '__exit__')
            return efunc(exc_type, exc_value, traceback)
        else:
            self.pop_.wait()
            if exc_type or exc_value or traceback:
                return False
            else:
                return True


def run_command(command, do_popen=False, turn_on_commands=True,
                single_line=False):
    """ wrapper around os.system """
    if not turn_on_commands:
        print(command)
        return command
    elif do_popen:
        if single_line:
            with PopenWrapperClass(command) as pop_:
                return pop_.read()
        else:
            return PopenWrapperClass(command)
    else:
        return call(command, shell=True)


def get_md5(fname):
    """ get md5sum for file """
    if not os.path.exists(fname):
        return None
    output = run_command('md5sum "%s"' % fname, do_popen=True,
                         single_line=True).split()[0]
    return output


def openurl(url_):
    """ wrapper around requests.get.text simulating urlopen """
    requests.packages.urllib3.disable_warnings()

    urlout = requests.get(url_)
    if urlout.status_code != 200:
        print('something bad happened %d' % urlout.status_code)
        raise HTTPError
    return urlout.text.split('\n')


def dump_to_file(url, outfile):
    """ dump url to file """
    from contextlib import closing
    requests.packages.urllib3.disable_warnings()
    with closing(requests.get(url, stream=True)) as url_:
        for chunk in url_.iter_content():
            outfile.write(chunk)
    return True


def cleanup_path(orig_path):
    """ cleanup path string using escape character """
    chars_to_escape = ' ()"[]&,!;$' + "'"
    for ch_ in chars_to_escape:
        orig_path = orig_path.replace(ch_, r'\%c' % ch_)
    return orig_path


def test_run_command():
    """ test run_command """
    cmd = 'echo "HELLO"'
    out = run_command(cmd, do_popen=True, single_line=True).strip()
    print(out, cmd)
    assert out == b'HELLO'


def test_cleanup_path():
    """ test cleanup_path """
    INSTR = '/home/ddboline/THIS TEST PATH (OR SOMETHING LIKE IT) ' \
            '[OR OTHER!] & ELSE $;,""'
    OUTSTR = r'/home/ddboline/THIS\ TEST\ PATH\ \(OR\ SOMETHING\ LIKE\ ' \
             r'IT\)\ \[OR\ OTHER\!\]\ \&\ ELSE\ \$\;\,\"\"'
    print(cleanup_path(INSTR))
    assert cleanup_path(INSTR) == OUTSTR


def test_get_md5():
    """ test get_md5 """
    import tempfile
    with tempfile.NamedTemporaryFile() as tfi:
        tfi.write(b'HELLO\n')
        tfi.flush()
        out = get_md5(tfi.name)
        assert out == b'0084467710d2fc9d8a306e14efbe6d0f'


class OpenPostgreSQLsshTunnel(object):
    """ Class to let us open an ssh tunnel, then close it when done """
    def __init__(self, port=5432):
        self.tunnel_process = 0
        self.postgre_port = 5432
        self.remote_port = port

    def __enter__(self):
        if HOSTNAME != 'dilepton-tower':
            self.postgre_port = self.remote_port
            _cmd = 'ssh -N -L localhost:%d' % self.remote_port + \
                   ':localhost:5432 ddboline@ddbolineathome.mooo.com'
            args = shlex.split(_cmd)
            self.tunnel_process = Popen(args, shell=False)
            time.sleep(5)
        return self.postgre_port

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tunnel_process:
            self.tunnel_process.kill()
        if exc_type or exc_value or traceback:
            return False
        else:
            return True
