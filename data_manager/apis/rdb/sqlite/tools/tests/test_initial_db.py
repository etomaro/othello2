import pytest 
import unittest 
import os

from data_manager.apis.rdb.sqlite.tools.initial_db import initial_db
from data_manager.apis.rdb.sqlite.settings import TEST_DB_PATH



class TestInitialDb(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        # テスト用DBを削除
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        
        # talbeの存在確認クエリ
        self._query_is_exist_table = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        # テーブルの全データを取得
        self._query_select_all = lambda table_name: f"SELECT * FROM {table_name};"
    
    def tearDown(self):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_initial_db(self):
        """
        [DB存在してない]
        1. is_delete=False: DBが作成されていること
        2. is_delete=True: エラーにならずDBが作成されていること
        [DBが存在している]
        3. is_delete=False: 何も変更されないこと(データが初期化されていないこと)
        4. is_delete=True: データが初期化されていること
        """
        # 1. is_delete=False: DBが作成されていること
        conn = initial_db(db_path=TEST_DB_PATH, is_delete=False)
        
        # DBが作成されていること
        self.assertTrue(os.path.exists(TEST_DB_PATH))
        # テーブルが作成されていること
        res_tables = conn.execute(self._query_is_exist_table, ("states",)).fetchone()
        self.assertTrue(res_tables)
        # データが初期化されていること
        # res_datas = conn.execute(self._query_select_all, ("states", )).fetchone()
        # self.assertEqual([], res_datas)
        
        print("iwamoto")
        print(conn.execute(self._query_select_all("states")))
        print("kaito")

        
        