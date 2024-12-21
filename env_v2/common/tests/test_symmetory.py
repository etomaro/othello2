import unittest

from env_v2.common.symmetory import (
    normalization, _reverse, _horizontal_flip, _transpose,
    _rotate90, _rotate180, _rotate270, _transformations
)

class TestSymmetory(unittest.TestCase):
    """
    テストデータはtest_base_symmetory.pyを参考
    """
    
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

    def get_datas_symmetory(self):
        """
        reverse,horizontal_flip,transpose,rotate90,rotate180,rotate270の
        テストデータと期待値を作成する

        1. board=0xffffffffffffffff
        2. board=0x0
        3. 

        returns:
          [
            {
              "board": "",
              "exp_reverse": "",
              "exp_horizontal_flip": "",
              "exp_transpose": "",
              "exp_rotate90": "",
              "exp_rotate180": "",
              "exp_rotate270": ""
            },...
          ]
        """
        datas = [
            # 1. board=0xffffffffffffffff
            {
                "board": 0xffffffffffffffff,
                "exp_reverse": 0xffffffffffffffff,
                "exp_horizontal_flip": 0xffffffffffffffff,
                "exp_transpose": 0xffffffffffffffff,
                "exp_rotate90": 0xffffffffffffffff,
                "exp_rotate180": 0xffffffffffffffff,
                "exp_rotate270": 0xffffffffffffffff,
            },
            # 2. board=0x0
            {
                "board": 0x0,
                "exp_reverse": 0x0,
                "exp_horizontal_flip": 0x0,
                "exp_transpose": 0x0,
                "exp_rotate90": 0x0,
                "exp_rotate180": 0x0,
                "exp_rotate270": 0x0,
            },
            # 3. f000000000000000
            {
                "board": 0xf000000000000000,
                "exp_reverse": 0x000000000000000f,
                "exp_horizontal_flip": 0x0f00000000000000,
                "exp_transpose": 0x8080808000000000,
                "exp_rotate90": 0x0101010100000000,
                "exp_rotate180": 0x000000000000000f,
                "exp_rotate270": 0x0000000080808080,
            },
            # 4. aa00000000000000
            {
                "board": 0xaa00000000000000,
                "exp_reverse": 0x0000000000000055,
                "exp_horizontal_flip": 0x5500000000000000,
                "exp_transpose": 0x8000800080008000,
                "exp_rotate90": 0x0100010001000100,
                "exp_rotate180": 0x0000000000000055,
                "exp_rotate270": 0x0080008000800080,
            },
            # 5. 0xfffefcf8f0e0c080
            {
                "board": 0xfffefcf8f0e0c080,
                "exp_reverse": 0x0103070f1f3f7fff,
                "exp_horizontal_flip": 0xff7f3f1f0f070301,
                "exp_transpose": 0xfffefcf8f0e0c080,
                "exp_rotate90": 0xff7f3f1f0f070301,
                "exp_rotate180": 0x0103070f1f3f7fff,
                "exp_rotate270": 0x80c0e0f0f8fcfeff,
            },
            # 6. 0x3563c9f006eda7c7
            {
                "board": 0x3563c9f006eda7c7,
                "exp_reverse": 0xe3e5b7600f93c6ac,
                "exp_horizontal_flip": 0xacc6930f60b7e5e3,
                "exp_transpose": 0x3775d690248f4be7,
                "exp_rotate90": 0xecae6b0924f1d2e7,
                "exp_rotate180": 0xe3e5b7600f93c6ac,
                "exp_rotate270": 0xe74b8f2490d67537,
            },
            # 7. 0xb1d36a8f6ab6c12f
            {
                "board": 0xb1d36a8f6ab6c12f,
                "exp_reverse": 0xf4836d56f156cb8d,
                "exp_horizontal_flip": 0x8dcb56f1566d83f4,
                "exp_transpose": 0xd66aadc439157dd3,
                "exp_rotate90": 0x6b56b5239ca8becb,
                "exp_rotate180": 0xf4836d56f156cb8d,
                "exp_rotate270": 0xd37d1539c4ad6ad6,
            },
            # 8. 0x143f7e904f0e66e6
            {
                "board": 0x143f7e904f0e66e6,
                "exp_reverse": 0x676670f2097efc28,
                "exp_horizontal_flip": 0x28fc7e09f2706667,
                "exp_transpose": 0x112b63f06cef6f48,
                "exp_rotate90": 0x88d4c60f36f7f612,
                "exp_rotate180": 0x676670f2097efc28,
                "exp_rotate270": 0x486fef6cf0632b11,
            },
        ]

        return datas        

    def test_datas_transformations(self):
        """
        transformationsのテストデータと期待値を作成する

        """
        datas = self.get_datas_symmetory()
        for data in datas:
            board = data["board"]
            # reverse
            self.assertEqual(data["exp_reverse"], _reverse(board))
            # horizontal_flip
            self.assertEqual(data["exp_horizontal_flip"], _horizontal_flip(board))
            # transpose
            self.assertEqual(data["exp_transpose"], _transpose(board))
            # rotate90
            self.assertEqual(data["exp_rotate90"], _rotate90(board))
            # rotate180
            self.assertEqual(data["exp_rotate180"], _rotate180(board))
            # rotate270
            self.assertEqual(data["exp_rotate270"], _rotate270(board))
        
    def test_symmetory(self):
        self.assertEqual(1,1)