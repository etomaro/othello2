import pytest
import unittest

from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.symmetory.symmetory import (_get_y, _get_x, _get_right_z, _get_left_z,
                                        _get_rotato90, _get_rotato180, _get_rotato270)


class TestSymmetry(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self._env = Env2(is_out_game_info=False, is_out_board=False)
    
    def tearDown(self) -> None:
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    @staticmethod
    def _print_board(board: int):
        """
        debug用
        boardを64桁にして視覚的にprint出力する
        """
        result = format(board, '64b')  # 2進数で64桁で0で穴埋め
        out = "\n"
        for i, value in enumerate(result):
            if int(i)%8==7:
                out += f"{value}\n"
            else:
                out += value
        print(out)
        
    def test_get_y(self):
        """
        1000 0000
        0100 0000
        0010 0000
        0001 0000
        0000 1000
        0000 0100
        0000 0010
        0000 0001
        ↓
        0000 0001
        0000 0010
        0000 0100
        0000 1000
        0001 0000
        0010 0000
        0100 0000
        1000 0000
        """
        board =0x8040201008040201
        exp = 0x0102040810204080
        result = _get_y(board)
        self.assertEqual(exp, result)
    
    def test_get_x(self):
        """
        1000 0000
        0100 0000
        0010 0000
        0001 0000
         
        0000 1000
        0000 0100
        0000 0010
        0000 0001
        ↓
        0000 0001
        0000 0010
        0000 0100
        0000 1000
        
        0001 0000
        0010 0000
        0100 0000
        1000 0000
        """
        board =0x8040201008040201
        exp = 0x0102040810204080
        result = _get_x(board)
        self.assertEqual(exp, result)
    
    def test_get_right_z(self):
        """
        1111 1111
        1111 1110
        1111 1100
        1111 1000
        1111 0000
        1110 0000
        1100 0000
        1000 0000
        ↓
        0000 0001
        0000 0011
        0000 0111
        0000 1111
        0001 1111
        0011 1111
        0111 1111
        1111 1111
        """
        board =0xfffefcf8f0e0c080
        exp = 0x0103070f1f3f7fff
        result = _get_right_z(board)
        self.assertEqual(exp, result)
    
    def test_get_left_z(self):
        """
        1111 1111
        0111 1111
        0011 1111
        0001 1111
        0000 1111
        0000 0111
        0000 0011
        0000 0001
        ↓
        1000 0000
        1100 0000
        1110 0000
        1111 0000
        1111 1000
        1111 1100
        1111 1110
        1111 1111
        """
        board =0xff7f3f1f0f070301
        exp = 0x80c0e0f0f8fcfeff
        result = _get_left_z(board)
        self.assertEqual(exp, result)
    
    def test_get_rotato90(self):
        """
        1111 1111
        1111 1111
        1111 1111
        1111 1111
        0000 0000
        0000 0000
        0000 0000
        0000 0000
        ↓
        0000 1111
        0000 1111
        0000 1111
        0000 1111
        0000 1111
        0000 1111
        0000 1111
        0000 1111
        """
        board = 0xffffffff00000000
        exp = 0x0f0f0f0f0f0f0f0f
        result = _get_rotato90(board)
        self.assertEqual(exp, result)

    def test_get_rotato180(self):
        """
        1111 1111
        1111 1111
        1111 1111
        1111 1111
        0000 0000
        0000 0000
        0000 0000
        0000 0000
        ↓
        0000 0000
        0000 0000
        0000 0000
        0000 0000
        1111 1111
        1111 1111
        1111 1111
        1111 1111
        """
        board = 0xffffffff00000000
        exp = 0x00000000ffffffff
        result = _get_rotato180(board)
        self.assertEqual(exp, result)
    
    def test_get_rotato270(self):
        """
        1111 1111
        1111 1111
        1111 1111
        1111 1111
        0000 0000
        0000 0000
        0000 0000
        0000 0000
        ↓
        1111 0000
        1111 0000
        1111 0000
        1111 0000
        1111 0000
        1111 0000
        1111 0000
        1111 0000
        """
        board = 0xffffffff00000000
        exp = 0xf0f0f0f0f0f0f0f0
        result = _get_rotato270(board)
        self.assertEqual(exp, result)
    