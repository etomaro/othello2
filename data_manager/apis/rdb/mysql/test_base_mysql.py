"""
MYSQLテスト用ベースクラス
"""
import unittest

from data_manager.apis.rdb.mysql.tools.initial_db import initial_db
from data_manager.apis.rdb.mysql.settings import (
    HOST_TEST, DB_NAME_TEST, USER_TEST, PASS_TEST, PORT_TEST
)


class TestBaseMysql(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self._host = HOST_TEST
        self._user = USER_TEST 
        self._db_name =DB_NAME_TEST 
        self._port = PORT_TEST 
        self._password = PASS_TEST
        
        self.settings = {
            "host": self._host,
            "user": self._user,
            "password": self._password,
            "port": self._port,
            "db_name": self._db_name
        }
        initial_db(self.settings, is_delete=True)
    
    def tearDown(self):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    