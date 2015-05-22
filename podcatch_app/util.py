#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
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
    try:
        from ssl import SSLContext, PROTOCOL_TLSv1
    except ImportError:
        SSLContext = None
        PROTOCOL_TLSv1 = None
    from urllib2 import urlopen
    
    if SSLContext is None:
        return urlopen(url_)
    else:
        gcontext = SSLContext(PROTOCOL_TLSv1)
        return urlopen(url_, context=gcontext)

def cleanup_path(orig_path):
    ''' cleanup path string using escape character '''
    return orig_path.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')\
                    .replace('\'', '\\\'').replace('[', '\[')\
                    .replace(']', '\]').replace('"', '\"').replace("'", "\'")\
                    .replace('&', '\&').replace(',', '\,').replace('!', '\!')\
                    .replace(';', '\;').replace('$', '\$')
