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
import hashlib
import requests
from StringIO import StringIO
import lxml.etree

from podcatch_app.podcatch_class import Podcasts, Episodes
from podcatch_app.postgres_dump import (connect_postgres, dump_postgres_memory,
                                        save_postgres)

from podcatch_app.util import dump_to_file, get_md5, OpenPostgreSQLsshTunnel

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
                if _pep.epfname() not in cur_urls:
                    yield _pep
                elif _pep.epfname() in cur_urls and \
                        cur_urls[_pep.epfname()].status \
                        not in ('Downloaded', 'Skipped'):
                    yield _pep
            _pep = Episodes()
            _pep.title = unicode(line.text).encode(errors='replace')
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
            (_pep.epfname() not in cur_urls) or
            (_pep.epfname() in cur_urls and
             cur_urls[_pep.epfname()].status not in
             ('Downloaded', 'Skipped'))):
        yield _pep


def podcatch(args, port=5432):
    _con = connect_postgres(port=port)
    podcasts = dump_postgres_memory(dbcon=_con, dumpclass=Podcasts)
    episodes = dump_postgres_memory(dbcon=_con, dumpclass=Episodes)

#    cur_urls = {ep.epurl: ep for ep in episodes}
    cur_urls = {ep.epfname(): ep for ep in episodes}

    epids = [ep.episodeid for ep in episodes]
    purls = []
    newepid = max(epids)
    for p in podcasts:
        resp = requests.get(p.feedurl)
        purls.extend(list(parse_feed(lxml.etree.parse(StringIO(resp.content)).iter(),
                                     cur_urls, newepid, p)))
    for ep in purls:
#        if ep.title.startswith('Bugle') and ep.title.split()[1].isdigit():
#            print(ep)
#            md5 = hashlib.md5()
#            md5.update(str(ep))
#            ep.epguid = md5.hexdigest()
#            ep.status = u'Skipped'
#            ep.epfailedattempts = 0
#            print(save_postgres(ep))
#            with _con.begin():
#                _con.execute(save_postgres(ep))
#            continue

        fname = ep.epfname()

        with open(fname, 'wb') as outfile:
            dump_to_file(ep.epurl, outfile)
        ep.epguid = get_md5(fname)
        if any(ep.epguid == ep_.epguid for ep_ in episodes):
            continue

        print(save_postgres(ep))
        print(os.stat(fname))
        if os.stat(fname).st_size > 0:
            dest = '%s/%s' % (OUTPUT_DIRECTORIES[ep.castid], fname)
            if not os.path.exists(dest):
                os.rename(fname, dest)
            else:
                os.remove(fname)
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
