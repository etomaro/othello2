import pytest
import unittest
import numpy as np


from env_v2.env_by_numpy import get_actionables_parallel, step_parallel, get_actions
from env_v2.symmetory.symmetory import get_symmetory_for_anality_batch

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
        actionables = get_actionables_parallel(states)
        exp = np.array([0x102004080000, 0x400140000])
        np.testing.assert_array_equal(exp,actionables)  # numpyのテスト関数(順序もテスト内)
    
    def test_get_actions(self):
        """
        [テストデータ]
        1. [0x810000000, 0x1008000000, 0]: 
                [
                   [0x810000000, 0x1008000000, 0, 0b100000000000000000000000000000000000000000000],
                   [0x810000000, 0x1008000000, 0, 0b000000010000000000000000000000000000000000000],
                   [0x810000000, 0x1008000000, 0, 0b000000000000000000100000000000000000000000000],
                   [0x810000000, 0x1008000000, 0, 0b000000000000000000000000010000000000000000000],
                ]
        2. [0x818080000, 0x1000000000, 1]: 
                [
                   [0x818080000, 0x1000000000, 1, 0b10000000000000000000000000000000000],
                   [0x818080000, 0x1000000000, 1, 0b00000000000000100000000000000000000],
                   [0x818080000, 0x1000000000, 1, 0b00000000000000001000000000000000000],
                ]
        """
        black_board1, white_board1, player_id1 = 0x810000000, 0x1008000000, 0
        black_board2, white_board2, player_id2 = 0x818080000, 0x1000000000, 1
        states = [
            [black_board1, white_board1, player_id1],
            [black_board2, white_board2, player_id2]
        ]
        #　実行
        actions = get_actions(states)
        exp = [
            [0x810000000, 0x1008000000, 0, 0b100000000000000000000000000000000000000000000],
            [0x810000000, 0x1008000000, 0, 0b000000010000000000000000000000000000000000000],
            [0x810000000, 0x1008000000, 0, 0b000000000000000000100000000000000000000000000],
            [0x810000000, 0x1008000000, 0, 0b000000000000000000000000010000000000000000000],
            [0x818080000, 0x1000000000, 1, 0b10000000000000000000000000000000000],
            [0x818080000, 0x1000000000, 1, 0b00000000000000100000000000000000000],
            [0x818080000, 0x1000000000, 1, 0b00000000000000001000000000000000000],
        ]
        self.assertEqual(exp, actions)  # numpyのテスト関数(順序もテスト内)
    
    def test_step_parallel(self):
        """
        [テストデータ]
        (black_board, white_board, player_id, action): (next_black_board, next_white_board, next_player_id)
        1. 0x810000000, 0x1008000000, 0, 0x80000: 0x818080000, 0x1000000000, 1
        2. 0x810000000, 0x1008000000, 0, 0x4000000: 0x81c000000, 0x1000000000, 1
        3. 0x81c000000, 0x1000000000, 1, 0x40000: 0x814000000, 0x1008040000, 0
        """
        dummy = np.array([0,0,0])
        states = np.array([
            [0x810000000, 0x1008000000, 0, 0x80000],
            [0x810000000, 0x1008000000, 0, 0x4000000],
            [0x81c000000, 0x1000000000, 1, 0x40000]
        ])
        # 実行
        next_states = step_parallel(states, dummy)
        # テスト
        # 関数として担保されている対称性を利用
        exp_bb_board1, exp_wb_board1 = get_symmetory_for_anality_batch(0x818080000, 0x1000000000)
        exp_bb_board2, exp_wb_board2 = get_symmetory_for_anality_batch(0x81c000000, 0x1000000000)
        exp_bb_board3, exp_wb_board3 = get_symmetory_for_anality_batch(0x814000000, 0x1008040000)
        exp = np.array([
            [exp_bb_board1, exp_wb_board1, 1],
            [exp_bb_board2, exp_wb_board2, 1],
            [exp_bb_board3, exp_wb_board3, 0],
        ])  
        np.testing.assert_array_equal(exp, next_states)

