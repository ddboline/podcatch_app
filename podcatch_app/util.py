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
    ''' cleanup path string using escape character '''
    return orig_path.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')\
                    .replace('\'', '\\\'').replace('[', '\[')\
                    .replace(']', '\]').replace('"', '\"').replace("'", "\'")\
                    .replace('&', '\&').replace(',', '\,').replace('!', '\!')\
                    .replace(';', '\;').replace('$', '\$')
