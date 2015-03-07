#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    podcatching app
'''
import os

from podcatch_app.podcatch_class import Podcasts, Episodes
from podcatch_app.sqlite_dump import connect_sqlite, dump_sqlite_memory

from urllib2 import urlopen

import lxml.etree

def add_podcast():
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    for pod in podcasts:
        print pod
    #pod = Podcasts(castid=24, castname=u'Welcome to Night Vale', feedurl=u'http://nightvale.libsyn.com/rss', pcenabled=1, lastupdate=0, lastattempt=0, failedattempts=0)
    #_con.execute(pod.sql_insert_string())

def podcatch(args):
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    cur_urls = {}
    epids = []
    for ep in episodes:
        cur_urls[ep.epurl] = ep
        if ep.episodeid not in epids:
            epids.append(ep.episodeid)

    urls_to_download = []
    purls = []
    curtitle = ''
    newepid = sorted(epids)[-1]
    for p in podcasts:
        _url = urlopen(p.feedurl)
        _pep = Episodes()
        #for line in _url:
            #print line.strip()
        #exit(0)
        for line in lxml.etree.parse(_url).iter():
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
                    _pep.eplength = int(val)
                if key == 'type':
                    _pep.enctype = val

    for ep in purls:
        #print ep.sql_insert_string()
        os.system('wget %s' % ep.epurl)
        ep.status = u'Downloaded'
        ep.epfailedattempts = 0
        _con.execute(ep.sql_insert_string())
        #exit(0)

    return

if __name__ == '__main__':
    #add_podcast()
    podcatch(os.sys.argv)
