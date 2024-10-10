import pytest 
import unittest
from unittest.mock import patch, MagicMock
import os

from data_manager.apis.rdb.sqlite.tools.initial_db import initial_db
from data_manager.apis.rdb.sqlite.settings import TEST_DB_PATH
from data_manager.apis.rdb.sqlite.states import States


class TestStates(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self._db_path = TEST_DB_PATH
        self._conn = initial_db(TEST_DB_PATH, is_delete=True)
        self._cursor = self._conn.cursor()
        self._states_db = States(self._conn)
        
        # query
        self._query_where_hash = "SELECT * FROM states WHERE hash = ?"
    
    def tearDown(self):
        self._conn.close()
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_put(self):
        """
        [重複許容無し]
        1. 重複なし
        2. 重複あり
        [重複許容アリ]
        3. 重複無し
        4. 重複あり
        """
        # 1. 重複無し
        black, white, player = 0x0, 0x1, 0x1
        self._states_db.put(black, white, player)
        
        # 確認
        exp_hash_state = self._states_db.generate_hash(black, white, player)
        res = self._cursor.execute(
            self._query_where_hash,
            (exp_hash_state, )
        ).fetchall()
        exp = [(1, black, white, player, exp_hash_state)]
        self.assertEqual(exp, res)
        
        # 2. 重複あり
        with self.assertRaises(Exception):
            # エラーになること
            self._states_db.put(black, white, player)
            
        # 3. 重複無し
        black2, white2, player2 = 0x1, 0x2, 0x0
        self._states_db.put(black2, white2, player2, is_allowed_duplicate=True)
        
        # 確認
        exp_hash_state2 = self._states_db.generate_hash(black2, white2, player2)
        res = self._cursor.execute(
            self._query_where_hash,
            (exp_hash_state2, )
        ).fetchall()
        exp = [(2, black2, white2, player2, exp_hash_state2)]
        self.assertEqual(exp, res)
        
        # 4. 重複あり
        # エラーにならないこと
        self._states_db.put(black2, white2, player2, is_allowed_duplicate=True)
        res = self._cursor.execute(
            self._query_where_hash,
            (exp_hash_state2, )
        ).fetchall()
        exp = [(2, black2, white2, player2, exp_hash_state2)]
        self.assertEqual(exp, res)
        
    def test_get(self):
        """
        1. データが存在しない
        2. データが存在する
        """
        black, white, player = 0x0, 0x1, 0x1
        
        # 1. データが存在しない
        # 例外が起きること
        with self.assertRaises(Exception):
            self._states_db.get(black, white, player)
        
        # 2. データが存在する
        self._states_db.put(black, white, player)
        res = self._states_db.get(black, white, player)
        
        exp_state_hash = self._states_db.generate_hash(black, white, player)
        exp = {
            "black": black,
            "white": white,
            "player": player,
            "hash": exp_state_hash
        }
        self.assertEqual(exp, res)
    
    def test_get_all(self):
        """
        1. 0件
        2. 5件
        """
        # 1. 0件
        res = self._states_db.get_all()
        self.assertEqual([], res)
        
        # 5件
        exp = []
        for i in range(5):
            # put
            self._states_db.put(i, i, i)
            exp_hash_state = self._states_db.generate_hash(i, i, i)
            exp.append(
                {
                    "black": i,
                    "white": i,
                    "player": i,
                    "hash": exp_hash_state
                }
            )
        # exec
        res = self._states_db.get_all()
        self.assertEqual(exp, res)

    @patch("slite3.connect.commit")
    def test_bulk_insert(self, mock_commit):
        """
        1. 5件データ投入
        2. エラーが発生してロールバックされていること
        """
        # 1. 5件データ投入
        exps = []
        datas = []
        for i in range(5):
            exp_state_hash = self._states_db.generate_hash(i, i, i)
            datas.append((i, i, i))
            exps.append(
                {
                    "black": i,
                    "white": i,
                    "player": i,
                    "hash": exp_state_hash   
                }
            )
        # exec
        self._states_db.bulk_insert(datas)
        
        # 検証
        res = self._states_db.get_all()
        self.assertSetEqual(exps, res)
        
        # 2. エラーが発生してロールバックされていること
        mock_commit.side_effect = Exception("mock error")
        
        datas2 = []
        for i in range(5, 10):
            datas2.append((i, i, i))
            
        # exec
        with self.assertRaises(Exception):
            self._states_db.bulk_insert(datas2)
            
            # rollbackが呼ばれていること
            self.assertTrue(mock_commit.called)
        
        # 検証(5件のままであること)
        res = self._states_db.get_all()
        self.assertSetEqual(exps, res)
    
    def speed_test_bulk_insert(self):
        pass
