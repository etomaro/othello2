import pytest 
import unittest
from unittest.mock import patch, MagicMock
import mysql
from mysql.connector import errorcode

from data_manager.apis.rdb.mysql.tools.initial_db import (
    initial_db, connect_to_mysql)
from data_manager.apis.rdb.mysql.settings import (
    HOST_TEST, DB_NAME_TEST, USER_TEST, PASS_TEST, PORT_TEST
)
from data_manager.apis.rdb.mysql.test_base_mysql import TestBaseMysql


class TestInitialDb(TestBaseMysql):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        super().tearDown()
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass
    
    def test_connect_to_mysql(self):
        """
        1. 正常
        2. passが違う
        3. dbが存在しない
        """
        # 1. 正常. errorが発生しないこと
        conn = connect_to_mysql(
            self._host,
            self._user,
            self._password,
            self._port,
            self._db_name,
        )
        conn.close()
        
        # 2. passが違う
        with self.assertRaises(mysql.connector.Error) as ex:
            _ = connect_to_mysql(
                self._host,
                self._user,
                "UNKNOWN",  # passが違う
                self._port,
                self._db_name,
            )
        # エラーコードが一致していること
        self.assertEqual(errorcode.ER_ACCESS_DENIED_ERROR, ex.exception.errno)
        
        # 3. dbが存在しない
        with self.assertRaises(mysql.connector.Error) as ex:
            _ = connect_to_mysql(
                self._host,
                self._user,
                self._password,
                self._port, 
                "UNKNOWN",  # DB名が違う
            )
        # エラーコードが一致していること
        self.assertEqual(errorcode.ER_BAD_DB_ERROR, ex.exception.errno)
        
