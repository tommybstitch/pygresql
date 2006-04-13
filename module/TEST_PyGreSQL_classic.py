#!/usr/bin/env python

import sys, unittest
from pg import *

# We need a database to test against.  If LOCAL_PyGreSQL.py exists we will
# get our information from that.  Otherwise we use the defaults.
dbname = 'unittest'
dbhost = None
dbport = 5432

try: from LOCAL_PyGreSQL import *
except: pass

db = DB(dbname, dbhost, dbport)
db.query("SET DATESTYLE TO 'ISO'")
db.query("SET TIME ZONE 'EST5EDT'")

class utility_test(unittest.TestCase):
    def setUp(self):
        # create test tables if they don't exist
        for t in ('_test1', '_test2'):
            try: db.query("CREATE SCHEMA " + t)
            except: pass
            try: db.query("CREATE TABLE %s._test_schema "
							"(%s int PRIMARY KEY)" % (t, t))
            except: pass

        try: db.query("CREATE TABLE _test_schema "
                       "(_test int PRIMARY KEY, _i interval)")
        except: pass

        try: db.query("CREATE VIEW _test_vschema AS "
			"SELECT _test, 'abc'::text AS _test2  FROM _test_schema")
        except: pass

    def test_invalidname(self):
        """Make sure that invalid table names are caught"""

        self.failUnlessRaises(ProgrammingError, db.get_attnames, 'x.y.z')

    def test_schema(self):
        """Does it differentiate the same table name in different schemas"""

        # see if they differentiate the table names properly
        self.assertEqual(
            db.get_attnames('_test_schema'),
            {'_test': 'int', 'oid': 'int', '_i': 'date'}
        )

        self.assertEqual(
            db.get_attnames('public._test_schema'),
            {'_test': 'int', 'oid': 'int', '_i': 'date'}
        )

        self.assertEqual(
            db.get_attnames('_test1._test_schema'),
            {'_test1': 'int', 'oid': 'int'}
        )

        self.assertEqual(
            db.get_attnames('_test2._test_schema'),
            {'_test2': 'int', 'oid': 'int'}
        )

    def test_pkey(self):
        self.assertEqual(db.pkey('_test_schema'), '_test')
        self.assertEqual(db.pkey('public._test_schema'), '_test')
        self.assertEqual(db.pkey('_test1._test_schema'), '_test1')

    def test_get(self):
        try: db.query("INSERT INTO _test_schema VALUES (1234)")
        except: pass # OK if it already exists

        db.get('_test_schema', 1234)
        db.get('_test_schema', 1234, keyname = '_test')
        self.failUnlessRaises(KeyError, db.get, '_test_vschema', 1234)
        db.get('_test_vschema', 1234, keyname = '_test')

    def test_quote(self):
        from pg import _quote
        self.assertEqual(_quote(1, 'int'), "1")
        self.assertEqual(_quote(1, 'text'), "'1'")
        self.assertEqual(_quote(1, 'seq'), "1")
        self.assertEqual(_quote(1, 'decimal'), "1")
        self.assertEqual(_quote('1', 'int'), "1")
        self.assertEqual(_quote('1', 'text'), "'1'")
        self.assertEqual(_quote('1', 'seq'), "1")
        self.assertEqual(_quote('1', 'decimal'), "1")
        self.assertEqual(_quote(None, 'int'), "NULL")
        self.assertEqual(_quote(1, 'money'), "'1.00'")
        self.assertEqual(_quote('1', 'money'), "'1.00'")
        self.assertEqual(_quote(1.234, 'money'), "'1.23'")
        self.assertEqual(_quote('1.234', 'money'), "'1.23'")
        self.assertEqual(_quote(0, 'bool'), "'f'")
        self.assertEqual(_quote('', 'bool'), "NULL")
        self.assertEqual(_quote('f', 'bool'), "'f'")
        self.assertEqual(_quote('off', 'bool'), "'f'")
        self.assertEqual(_quote('no', 'bool'), "'f'")
        self.assertEqual(_quote(1, 'bool'), "'t'")
        self.assertEqual(_quote('1', 'bool'), "'t'")
        self.assertEqual(_quote('t', 'bool'), "'t'")
        self.assertEqual(_quote('on', 'bool'), "'t'")
        self.assertEqual(_quote('yes', 'bool'), "'t'")
        self.assertEqual(_quote('true', 'bool'), "'t'")
        self.assertEqual(_quote('y', 'bool'), "'t'")
        self.assertEqual(_quote('', 'date'), "NULL")
        self.assertEqual(_quote('', 'inet'), "NULL")
        self.assertEqual(_quote('', 'cidr'), "NULL")
        self.assertEqual(_quote('date', 'date'), "'date'")
        self.assertEqual(_quote('inet', 'inet'), "'inet'")
        self.assertEqual(_quote('cidr', 'cidr'), "'cidr'")
        self.assertEqual(_quote('', 'text'), "''")

if __name__ == '__main__':
    unittest.main()