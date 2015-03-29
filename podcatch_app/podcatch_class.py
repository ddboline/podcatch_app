#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Class representing podcasts, episodes tables in sqlite db
'''

class Podcasts(object):
    __tablename__ = 'podcasts'

    __columns__ = ['castid', 'castname', 'feedurl', 'pcenabled', 'lastupdate',
                   'lastattempt', 'failedattempts']

    def __init__(self, **kwargs):
        self.castname = ''
        self.feedurl = ''
        self.pcenabled = 1
        for col in self.__columns__:
            if col in kwargs:
                setattr(self, col, kwargs[col])
            else:
                setattr(self, col, 0)

    def __repr__(self):
        return '<podcasts(%s)>' % (', '.join(['%s=%s' % (x, getattr(self, x)) for x in self.__columns__]))

    def sql_insert_string(self):
        outstr = []
        outstr.append('INSERT INTO %s(%s)' % (self.__tablename__, ', '.join(self.__columns__)))
        valstr = []
        for col in self.__columns__:
            val = getattr(self, col)
            if type(val) == unicode:
                valstr.append("'%s'" % val.replace("'",''))
            elif type(val) == int:
                valstr.append('%s' % val)
            elif not val:
                valstr.append('NULL')
            else:
                valstr.append('%s' % val)
        outstr.append('VALUES (%s);' % ', '.join(valstr))
        return ' '.join(outstr)

class Episodes(object):
    __tablename__ = 'episodes'

    __columns__ = ['castid', 'episodeid', 'title', 'epurl', 'enctype',
                   'status', 'eplength', 'epfirstattempt', 'eplastattempt',
                   'epfailedattempts', 'epguid']

    def __init__(self, **kwargs):
        for col in self.__columns__:
            if col in kwargs:
                setattr(self, col, kwargs[col])
            else:
                setattr(self, col, 0)
        self.epfailedattempts = 0
        self.title = ''
        self.epurl = ''
        self.enctype = ''
        self.status = ''
        self.epguid = ''

    def __repr__(self):
        return '<episodes(%s)>' % (', '.join(['%s=%s' % (x, getattr(self, x)) for x in self.__columns__]))

    def sql_insert_string(self):
        outstr = []
        outstr.append('INSERT INTO %s(%s)' % (self.__tablename__, ', '.join(self.__columns__)))
        valstr = []
        for col in self.__columns__:
            val = getattr(self, col)
            if type(val) == unicode:
                valstr.append("'%s'" % val.replace("'",''))
            elif type(val) == int:
                valstr.append('%s' % val)
            elif not val:
                valstr.append('NULL')
            else:
                valstr.append('%s' % val)
        outstr.append('VALUES (%s);' % ', '.join(valstr))
        return ' '.join(outstr)
