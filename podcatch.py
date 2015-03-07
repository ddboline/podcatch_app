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

OUTPUT_DIRECTORIES = {
    19: '/home/ddboline/Documents/mp3/The_Current_song_of_the_Day/',
    23: '/home/ddboline/Documents/podcasts/The_Bugle/',
    24: '/home/ddboline/Documents/podcasts/Welcome_to_Night_Vale/',}

def add_podcast():
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    for pod in podcasts:
        print pod
        print OUTPUT_DIRECTORIES[pod.castid]
    #pod = Podcasts(castid=24, castname=u'Welcome to Night Vale', feedurl=u'http://nightvale.libsyn.com/rss', pcenabled=1, lastupdate=0, lastattempt=0, failedattempts=0)
    #_con.execute(pod.sql_insert_string())

def podcatch(args):
    _con = connect_sqlite()
    podcasts = dump_sqlite_memory(sqlite_con=_con, dumpclass=Podcasts)
    episodes = dump_sqlite_memory(sqlite_con=_con, dumpclass=Episodes)

    #_con.execute('DELETE FROM episodes WHERE title="1 - Pilot";')
    #_con.execute('UPDATE episodes SET status="Unknown" WHERE episodeid=1876;')

    cur_urls = {}
    epids = []
    for ep in episodes:
        cur_urls[ep.epurl] = ep
        #try:
            #print ep
        #except UnicodeEncodeError:
            #print ep.__repr__().encode(errors='ignore')
        if ep.episodeid not in epids:
            epids.append(ep.episodeid)
    #exit(0)
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

        if _pep.epurl:
            if _pep.epurl not in cur_urls:
                purls.append(_pep)
            elif _pep.epurl in cur_urls and \
                    cur_urls[_pep.epurl].status not in ('Downloaded', 'Skipped'):
                purls.append(_pep)

    for ep in purls:
        print ep.sql_insert_string()
        FNAME = os.path.basename(ep.epurl)
        #os.system('wget %s' % ep.epurl)
        
        with open(FNAME, 'wb') as outfile:
            urlout = urlopen(ep.epurl)
            if urlout.getcode() != 200:
                print('something bad happened %d' % urlout.getcode())
                exit(0)
            for line in urlout:
                outfile.write(line)

        print os.stat(FNAME)
        if os.stat(FNAME).st_size > 0:
            os.system('mv %s %s' % (FNAME, OUTPUT_DIRECTORIES[ep.castid]))
            ep.status = u'Downloaded'
            ep.epfailedattempts = 0
            _con.execute(ep.sql_insert_string())

    return

if __name__ == '__main__':
    #add_podcast()
    podcatch(os.sys.argv)
