"""
    This file is part of AminoPVR.
    Copyright (C) 2012  Ino Dekker

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import test_lib as test     # import test_lib before anything else from aminopvr!


class DBBasicTests( test.AminoPVRTestDBCase ):

    def setUp( self ):
        super( DBBasicTests, self ).setUp()
        self.db = test.db.DBConnection()

    def tearDown( self ):
        del self.db
        super( DBBasicTests, self ).tearDown()

    def test_select( self ):
        self.assertGreater( self.db.execute( "SELECT db_version FROM db_version" )[0]["db_version"], 0, "" )


if __name__ == '__main__':
    print "=================="
    print "STARTING - DB TESTS"
    print "=================="
    print "######################################################################"
    suite = unittest.TestLoader().loadTestsFromTestCase( DBBasicTests )
    unittest.TextTestRunner( verbosity=2 ).run( suite )
