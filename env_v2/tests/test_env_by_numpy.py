import pytest
import unittest
import numpy as np


from env_v2.env_by_numpy import get_initial_board, get_actionables


class TestEnv2ByNumpy(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self) -> None:
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
        
    def test_get_actionables(self):
        """
        [テストデータ]
        1. 0x810000000, 0x1008000000, 0: 0x102004080000
        2. 0x818080000, 0x1000000000, 1: 0x400140000
        """
        black_board1, white_board1, player_id1 = 0x810000000, 0x1008000000, 0
        black_board2, white_board2, player_id2 = 0x818080000, 0x1000000000, 1
        states = np.array([
            [black_board1, white_board1, player_id1],
            [black_board2, white_board2, player_id2]
        ])
        #　実行
        actionables = get_actionables(states)
        exp = np.array([0x102004080000, 0x400140000])
        np.testing.assert_array_equal(exp,actionables)  # numpyのテスト関数(順序もテスト内)
