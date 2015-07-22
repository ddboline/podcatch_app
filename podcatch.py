#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    podcatching app
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from podcatch_app.podcatch_class import Podcasts, Episodes
from podcatch_app.sqlite_dump import (connect_sqlite, dump_sqlite_memory,
                                      save_sqlite)

from podcatch_app.util import dump_to_file, get_md5

import lxml.etree

OUTPUT_DIRECTORIES = {
    19: '/home/ddboline/Documents/mp3/The_Current_song_of_the_Day/',
    23: '/home/ddboline/Documents/podcasts/The_Bugle/',
    24: '/home/ddboline/Documents/podcasts/Welcome_to_Night_Vale/',}

def add_podcast(cid=-1, cname='', furl=''):
    if cid == -1 and not cname and not furl:
        return
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    for pod in podcasts:
        print(pod)
        print(OUTPUT_DIRECTORIES[pod.castid])

    for ep in episodes:
        if cid != ep.castid:
            continue
        if furl == ep.epurl:
            return

    pod = Podcasts(castid=24, castname=u'Welcome to Night Vale',
                   feedurl=u'http://nightvale.libsyn.com/rss',
                   pcenabled=1, lastupdate=0, lastattempt=0, failedattempts=0)
    _con.execute(save_sqlite(pod))

def podcatch(args):
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    cur_urls = {}
    epids = []
    for ep in episodes:
        cur_urls[ep.epurl] = ep
        epids.append(ep.episodeid)
    purls = []
    newepid = sorted(set(epids))[-1]
    for p in podcasts:
        _pep = Episodes()
        for line in lxml.etree.parse(p.feedurl).iter():
            if line.tag == 'title':
                if _pep.epurl:
                    if _pep.epurl not in cur_urls:
                        purls.append(_pep)
                    elif _pep.epurl in cur_urls and \
                         cur_urls[_pep.epurl].status not in ('Downloaded', 'Skipped'):
                        purls.append(_pep)
                _pep = Episodes()
                _pep.title = unicode(line.text)
                _pep.castid = p.castid
                _pep.episodeid = newepid
                newepid += 1
            for key, val in line.items():
                val = unicode(val)
                if not _pep:
                    continue
                if key == 'url':
                    _pep.epurl = val
                if key == 'length':
                    if not val:
                        _pep.eplength = -1
                    else:
                        _pep.eplength = int(val)
                if key == 'type':
                    _pep.enctype = val

        if _pep.epurl:
            if _pep.epurl not in cur_urls:
                purls.append(_pep)
            elif _pep.epurl in cur_urls and \
                    cur_urls[_pep.epurl].status not in ('Downloaded', 'Skipped'):
                purls.append(_pep)

    for ep in purls:
        print(save_sqlite(ep))
        fname = os.path.basename(ep.epurl)

        with open(fname, 'wb') as outfile:
            dump_to_file(ep.epurl, outfile)
        ep.epguid = get_md5(fname)
        print(os.stat(fname))
        if os.stat(fname).st_size > 0:
            os.system('mv %s %s' % (fname, OUTPUT_DIRECTORIES[ep.castid]))
            ep.status = u'Downloaded'
            ep.epfailedattempts = 0
            _con.execute(save_sqlite(ep))
        else:
            print('bad file')
            os.remove(fname)
    return

if __name__ == '__main__':
    podcatch(os.sys.argv)
