#-*- coding: ISO-8859-1 -*-
# pysqlite2/test/transactions.py: tests transactions
#
# Copyright (C) 2004 Gerhard H�ring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import os, unittest
import pysqlite2.dbapi2 as sqlite

def get_db_path():
    return "testdb"

class TransactionTests(unittest.TestCase):
    def setUp(self):
        try:
            os.remove(get_db_path())
        except:
            pass

        self.con1 = sqlite.connect(get_db_path())
        self.cur1 = self.con1.cursor()

        self.con2 = sqlite.connect(get_db_path())
        self.cur2 = self.con2.cursor()

    def tearDown(self):
        self.cur1.close()
        self.con1.close()

        self.cur2.close()
        self.con2.close()

    def CheckDMLdoesAutoCommitBefore(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur1.execute("create table test2(j)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

    def CheckInsertStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 0)

    def CheckUpdateStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("update test set i=6")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchone()[0]
        self.failUnlessEqual(res, 5)

    def CheckDeleteStartsTransaction(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("delete from test")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

    def CheckToggleAutoCommit(self):
        self.cur1.execute("create table test(i)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.autocommit = True
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

        self.con1.autocommit = False
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

def suite():
    default_suite = unittest.makeSuite(TransactionTests, "Check")
    return unittest.TestSuite((default_suite,))

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    test()