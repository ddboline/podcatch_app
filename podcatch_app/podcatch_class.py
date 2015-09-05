#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Class representing podcasts, episodes tables in sqlite db
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

class Podcasts(object):
    tablename = 'podcasts'

    columns = ['castid', 'castname', 'feedurl', 'pcenabled', 'lastupdate',
                   'lastattempt', 'failedattempts']

    def __init__(self, **kwargs):
        self.castname = ''
        self.feedurl = ''
        self.pcenabled = 1
        for col in self.columns:
            if col in kwargs:
                setattr(self, col, kwargs[col])
            else:
                setattr(self, col, 0)

    def __repr__(self):
        return '<podcasts(%s)>' % (', '.join(['%s=%s' % (x, getattr(self, x))
                                   for x in self.columns]))

def test_podcasts():
    tdict = {'castid': '12345', 'castname': 'test',
             'feedurl': 'https://httpbin.org/html',
             'pcenabled': 'False', 'lastupdate': None,
             'lastattempt': None, 'failedattempts': 0}
    tmp = '%s' % Podcasts(**tdict)
    test = '<podcasts(castid=12345, castname=test, ' + \
           'feedurl=https://httpbin.org/html, pcenabled=False, ' + \
           'lastupdate=None, lastattempt=None, failedattempts=0)>'
    assert tmp == test

class Episodes(object):
    tablename = 'episodes'

    columns = ['castid', 'episodeid', 'title', 'epurl', 'enctype',
                   'status', 'eplength', 'epfirstattempt', 'eplastattempt',
                   'epfailedattempts', 'epguid']

    def __init__(self, **kwargs):
        self.epfailedattempts = 0
        self.title = ''
        self.epurl = ''
        self.enctype = ''
        self.status = ''
        self.epguid = ''
        for col in self.columns:
            if col in kwargs:
                setattr(self, col, kwargs[col])
            else:
                setattr(self, col, 0)

    def __repr__(self):
        return '<episodes(%s)>' % (', '.join(['%s=%s' % (x, getattr(self, x))
                                   for x in self.columns]))

def test_episodes():
    tdict = {'castid': '12345', 'castname': 'test',
             'feedurl': 'https://httpbin.org/html',
             'pcenabled': 'False', 'lastupdate': None,
             'lastattempt': None, 'failedattempts': 0,
             'episodeid': 12345, 'title': 'test',
             'epurl': 'https://httpbin.org/html', 'enctype': 'test',
             'status': 'bad', 'eplength': 12345, 'epfirstattempt': None,
             'eplastattempt': None, 'epfailedattempts': 0, 'epguid': 12345}

    tmp = '%s' % Episodes(**tdict)
    test = '<episodes(castid=12345, episodeid=12345, title=test, ' + \
           'epurl=https://httpbin.org/html, enctype=test, status=bad, ' + \
           'eplength=12345, epfirstattempt=None, eplastattempt=None, ' + \
           'epfailedattempts=0, epguid=12345)>'
    assert tmp == test