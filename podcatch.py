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
from podcatch_app.postgres_dump import (connect_postgres, dump_postgres_memory,
                                        save_postgres)

from podcatch_app.util import dump_to_file, get_md5, OpenPostgreSQLsshTunnel

import lxml.etree

OUTPUT_DIRECTORIES = {
    19: '/home/ddboline/Documents/mp3/The_Current_song_of_the_Day/',
    23: '/home/ddboline/Documents/podcasts/The_Bugle/',
    24: '/home/ddboline/Documents/podcasts/Welcome_to_Night_Vale/'}


def add_podcast(cid=-1, cname='', furl='', port=5432):
    if cid == -1 and not cname and not furl:
        return
    _con = connect_postgres(port=port)
    podcasts = dump_postgres_memory(dbcon=_con, dumpclass=Podcasts)
    episodes = dump_postgres_memory(dbcon=_con, dumpclass=Episodes)

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
    with _con.begin():
        _con.execute(save_postgres(pod))


def parse_feed(feed_it, cur_urls, newepid, pod_):
    _pep = Episodes()
    for line in feed_it:
        if line.tag == 'title':
            if _pep.epurl:
                if os.path.basename(_pep.epurl) not in cur_urls:
                    yield _pep
                elif os.path.basename(_pep.epurl) in cur_urls and \
                        cur_urls[os.path.basename(_pep.epurl)].status \
                        not in ('Downloaded', 'Skipped'):
                    yield _pep
            _pep = Episodes()
            _pep.title = unicode(line.text)
            _pep.castid = pod_.castid
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

    if _pep.epurl and (
            (os.path.basename(_pep.epurl) not in cur_urls) or
            (os.path.basename(_pep.epurl) in cur_urls and
             cur_urls[os.path.basename(_pep.epurl)].status not in
             ('Downloaded', 'Skipped'))):
        yield _pep


def podcatch(args, port=5432):
    _con = connect_postgres(port=port)
    podcasts = dump_postgres_memory(dbcon=_con, dumpclass=Podcasts)
    episodes = dump_postgres_memory(dbcon=_con, dumpclass=Episodes)

#    cur_urls = {ep.epurl: ep for ep in episodes}
    cur_urls = {os.path.basename(ep.epurl): ep for ep in episodes}

    epids = [ep.episodeid for ep in episodes]
    purls = []
    newepid = max(epids)
    for p in podcasts:
        purls.extend(list(parse_feed(lxml.etree.parse(p.feedurl).iter(),
                                     cur_urls, newepid, p)))
    for ep in purls:
        fname = os.path.basename(ep.epurl)

        with open(fname, 'wb') as outfile:
            dump_to_file(ep.epurl, outfile)
        ep.epguid = get_md5(fname)
        if any(ep.epguid == ep_.epguid for ep_ in episodes):
            continue
        print(save_postgres(ep))
        print(os.stat(fname))
        if os.stat(fname).st_size > 0:
            os.system('mv %s %s' % (fname, OUTPUT_DIRECTORIES[ep.castid]))
            ep.status = u'Downloaded'
            ep.epfailedattempts = 0
            with _con.begin():
                _con.execute(save_postgres(ep))
        else:
            print('bad file')
            os.remove(fname)
    return

if __name__ == '__main__':
    with OpenPostgreSQLsshTunnel(port=5433) as pport:
        podcatch(os.sys.argv, port=pport)
