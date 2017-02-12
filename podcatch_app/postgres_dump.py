#!/usr/bin/python
'''
    Dump postgres db
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import create_engine
from .util import POSTGRESTRING


def connect_postgres(port=5432, dbname='podcatch'):
    postgre_str = '%s:%d/%s' % (POSTGRESTRING, port, dbname)
    engine = create_engine(postgre_str, echo=False)
    con = engine.connect()
    return con


def dump_postgres_memory(dbcon=None, dumpclass=None):
    if dbcon is None:
        dbcon = connect_postgres()

    outlist = []
    query = 'SELECT %s from %s;' % (','.join(dumpclass.columns), dumpclass.tablename)
    for line in dbcon.execute(query):
        classinst = dumpclass()
        if len(line) != len(dumpclass.columns):
            print('something is not right')
        for n in range(len(line)):
            setattr(classinst, dumpclass.columns[n], line[n])
        outlist.append(classinst)
    return outlist


def save_postgres(dumpclass=None):
    outstr = []
    outstr.append('INSERT INTO %s(%s)' % (dumpclass.tablename, ', '.join(dumpclass.columns)))
    valstr = []
    for col in dumpclass.columns:
        val = getattr(dumpclass, col)
        if type(val) == unicode or type(val) == str:
            valstr.append("'%s'" % val.replace("'", ''))
        elif type(val) == int:
            valstr.append('%s' % val)
        elif not val:
            valstr.append('NULL')
        else:
            valstr.append('%s' % val)
    outstr.append('VALUES (%s);' % ', '.join(valstr))
    return ' '.join(outstr)
