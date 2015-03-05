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

    #_con.execute(u"INSERT INTO episodes(castid, episodeid, title, epurl, enctype, status, eplength, epfirstattempt, eplastattempt, epfailedattempts, epguid) VALUES (19, 1057, 'Twerps - Back to You', 'http://download.publicradio.org/podcast/minnesota/the_current/song_of_the_day/2015/03/03/20150303_twerps_back_to_you_128.mp3', 'audio/mpeg', 'Downloaded', 2434888, 0, 0, 0, NULL);")
    #exit(0)

    for ep in purls:
        os.system('wget %s' % ep.epurl)
        ep.status = u'Downloaded'
        ep.epfailedattempts = 0
        _con.execute(ep.sql_insert_string())
        #exit(0)

    return

if __name__ == '__main__':
    podcatch(os.sys.argv)
