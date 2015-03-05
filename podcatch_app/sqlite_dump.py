#!/usr/bin/python
'''
    Dump sqlite db
'''

import os
from sqlalchemy import create_engine

def connect_sqlite():
    engine = create_engine('sqlite:///podcatch.db', echo=False)
    con = engine.connect()
    return con

def dump_sqlite_memory(sqlite_con=None, dumpclass=None):
    dbcon = sqlite_con
    if not sqlite_con:
        dbcon = connect_sqlite()

    outlist = []
    sqlite_query = 'SELECT %s from %s;' % (','.join(dumpclass.__columns__),
                                           dumpclass.__tablename__)
    for line in dbcon.execute(sqlite_query):
        classinst = dumpclass()
        if len(line) != len(dumpclass.__columns__):
            print 'something is not right'
        for n in range(len(line)):
            setattr(classinst, dumpclass.__columns__[n], line[n])
        outlist.append(classinst)
    return outlist
