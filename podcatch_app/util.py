#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from subprocess import call, Popen, PIPE

HOMEDIR = os.getenv('HOME')

def run_command(command, do_popen=False, turn_on_commands=True):
    ''' wrapper around os.system '''
    if not turn_on_commands:
        print(command)
        return command
    elif do_popen:
        return Popen(command, shell=True, stdout=PIPE, close_fds=True).stdout
    else:
        return call(command, shell=True)

def get_md5(fname):
    if not os.path.exists(fname):
        return None
    output = run_command('md5sum "%s"' % fname,
                         do_popen=True).read().split()[0]
    return output

def openurl(url_):
    """ wrapper around requests.get.text simulating urlopen """
    import requests
    from requests import HTTPError
    requests.packages.urllib3.disable_warnings()

    urlout = requests.get(url_)
    if urlout.status_code != 200:
        print('something bad happened %d' % urlout.status_code)
        raise HTTPError
    return urlout.text.split('\n')

def dump_to_file(url_, outfile_):
    from contextlib import closing
    import requests
    requests.packages.urllib3.disable_warnings()
    with closing(requests.get(url_, stream=True)) as url_:
        for chunk in url_.iter_content(4096):
            outfile_.write(chunk)
    return True

def cleanup_path(orig_path):
    """ cleanup path string using escape character """
    chars_to_escape = ' ()"[]&,!;$' + "'"
    for ch_ in chars_to_escape:
        orig_path = orig_path.replace(ch_, r'\%c' % ch_)
    return orig_path

def test_run_command():
    cmd = 'echo "HELLO"'
    out = run_command(cmd, do_popen=True).read().strip()
    print(out, cmd)
    assert out == b'HELLO'

def test_cleanup_path():
    INSTR = '/home/ddboline/THIS TEST PATH (OR SOMETHING LIKE IT) [OR OTHER!] & ELSE $;,""'
    OUTSTR = r'/home/ddboline/THIS\ TEST\ PATH\ \(OR\ SOMETHING\ LIKE\ IT\)\ \[OR\ OTHER\!\]\ \&\ ELSE\ \$\;\,\"\"'
    print(cleanup_path(INSTR))
    assert cleanup_path(INSTR) == OUTSTR

def test_get_md5():
    import tempfile
    with tempfile.NamedTemporaryFile() as tfi:
        tfi.write(b'HELLO\n')
        tfi.flush()
        out = get_md5(tfi.name)
        assert out == b'0084467710d2fc9d8a306e14efbe6d0f'
