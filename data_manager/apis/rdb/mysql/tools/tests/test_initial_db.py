import mysql.connector
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
        conn, cursor = connect_to_mysql(
            self._host,
            self._user,
            self._password,
            self._port,
            self._db_name,
        )
        conn.close()
        cursor.close()
        
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
    
    def test_initial_db(self):
        """
        1. テーブルが存在している状態
        2. テーブルが存在してない状態
        3. データが削除確認
        """
        master_conn = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            port=self._port,
            database=self._db_name
        )
        master_cursor = master_conn.cursor()
        
        # 1. テーブルが存在している状態(TestBaseでinit_dbを起動しているので作成されているはず)
        _ = initial_db(self._settings, is_delete=False)
        master_cursor.execute(f"SHOW TABLES FROM {self._db_name}")
        res_tables = master_cursor.fetchall()
        self.assertEqual([("states", )], res_tables)
        
        # 2. テーブルが存在してない状態
        master_cursor.execute(f"DROP TABLE states")  # テーブル削除
        master_conn.commit()
        master_cursor.execute(f"SHOW TABLES FROM {self._db_name}")  # テーブルが削除されていること
        res_tables = master_cursor.fetchall()
        self.assertEqual([], res_tables)
        
        _ = initial_db(self._settings, is_delete=False)  # 実行
        master_cursor.execute(f"SHOW TABLES FROM {self._db_name}")
        res_tables = master_cursor.fetchall()
        self.assertEqual([("states", )], res_tables)  # テーブルが作成されていること
    
    def test_mysql_utils1(self):
        """Mysqlの仕様をテストする 
        1. 2つのコネクションとトランザクション
        """
        # 1. 2つのコネクションとトランザクション
        conn1 = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            port=self._port,
            database=self._db_name
        )
        cursor1 = conn1.cursor()

        conn2 = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            port=self._port,
            database=self._db_name
        )
        cursor2 = conn2.cursor()
        
        # データが登録されていないことを確認
        cursor1.execute("SELECT * FROM states;")
        res = cursor1.fetchall()
        self.assertEqual([], res)
        
        """
        1. cursor1でレコードを追加
        2. cursor1でレコードを取得
           -> レコード有
        3. cursor2でレコードを取得
           -> レコード無し
        4. cursor1でコミット
        5. cursor1でレコードを取得
        6. cursor2でレコードを取得
           -> レコード有
        """
        # 1. cursor1でレコードを追加
        cursor1.execute("INSERT INTO states (black, white, player, hash) VALUES (1,2,3,4)")
        # 2. cursor1でレコードを取得
        cursor1.execute("SELECT * FROM states;")
        res = cursor1.fetchall()
        self.assertEqual([(1,1,2,3,"4")], res)
        # 3. cursor2でレコードを取得
        cursor2.execute("SELECT * FROM states;")
        res = cursor2.fetchall()
        self.assertEqual([], res)
        # 4. cursor1でコミット
        conn1.commit()
        # 5. cursor1でレコードを取得
        cursor1.execute("SELECT * FROM states;")
        res = cursor1.fetchall()
        self.assertEqual([(1,1,2,3,"4")], res)
        # 6. cursor2でレコードを取得
        # TODO なぜかエラーになる
        # conn2.commit()
        cursor2.execute("SELECT * FROM states;")
        res = cursor2.fetchall()
        self.assertEqual([(1,1,2,3,"4")], res)
    
    def test_mysql_utils2(self):
        """Mysqlの仕様をテストする 
        1. 2連続でfetchall()する
        """
        conn1 = mysql.connector.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            port=self._port,
            database=self._db_name
        )
        cursor1 = conn1.cursor()
        
        # cursor1でレコードを追加
        cursor1.execute("INSERT INTO states (black, white, player, hash) VALUES (1,2,3,4)")
        # 1回目
        cursor1.execute("SELECT * FROM states;")
        res = cursor1.fetchall()
        self.assertEqual([(1,1,2,3,"4")], res)
        # 2回目
        cursor1.execute("SELECT * FROM states;")
        res = cursor1.fetchall()
        self.assertEqual([(1,1,2,3,"4")], res)
        