import unittest


class TestGosperHackWithStateBit(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # print("setUpClass")
        pass
    
    def setUp(self):
        # print("setup")
        pass
    
    def tearDown(self) -> None:
        # print("tearDown")
        pass
    
    @classmethod
    def tearDownClass(cls):
        # print("tearDownClass")
        pass
    
    """
    1. 件数テスト(※時間がかかるため60C(1-5)と60C(56-60)
    2. 既存の60Cgenerationを求めるものと計算結果が同じか
    3. 既存の60Cgenerationを求めるものとの速度調査
    """
    def test_tmp(self):
        self.assertTrue(True)