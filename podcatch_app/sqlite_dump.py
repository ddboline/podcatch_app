#!/usr/bin/python
'''
    Dump sqlite db
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import create_engine


def connect_sqlite(dbfile='podcatch.db'):
    engine = create_engine('sqlite:///%s' % dbfile, echo=False)
    con = engine.connect()
    return con


def dump_sqlite_memory(sqlite_con=None, dumpclass=None):
    dbcon = sqlite_con
    if not sqlite_con:
        dbcon = connect_sqlite()

    outlist = []
    sqlite_query = 'SELECT %s from %s;' % (','.join(dumpclass.columns), dumpclass.tablename)
    for line in dbcon.execute(sqlite_query):
        classinst = dumpclass()
        if len(line) != len(dumpclass.columns):
            print('something is not right')
        for n in range(len(line)):
            setattr(classinst, dumpclass.columns[n], line[n])
        outlist.append(classinst)
    return outlist


def save_sqlite(dumpclass=None):
    outstr = []
    outstr.append('INSERT INTO %s(%s)' % (dumpclass.tablename, ', '.join(dumpclass.columns)))
    valstr = []
    for col in dumpclass.columns:
        val = getattr(dumpclass, col)
        if isinstance(val, text_type):
            valstr.append("'%s'" % val.replace("'", ''))
        elif isinstance(val, int):
            valstr.append('%s' % val)
        elif not val:
            valstr.append('NULL')
        else:
            valstr.append('%s' % val)
    outstr.append('VALUES (%s);' % ', '.join(valstr))
    return ' '.join(outstr)
