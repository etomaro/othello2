import unittest
import itertools
import time

from common.n_C_r.json_utils import read_json_n_c_r
from common.bit_utils.gosper_hack_with_state_bit import get_60_c_r_by_gosper_hack_with_state_bit
from common.dt_utils import sec_to_str


CENTER_POS = [27, 28, 35, 36]
CENTER_POS_TUPLE = (27, 28, 35, 36)
NOT_CENTER_POS = [
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 29, 30, 31,
    32, 33, 34, 37, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62, 63
]

class TestGosperHackWithStateBit(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # print("setUpClass")
        pass
    
    def setUp(self):
        # print("setup")
        self._60_c_r = read_json_n_c_r(60)
    
    def tearDown(self) -> None:
        # print("tearDown")
        pass
    
    @classmethod
    def tearDownClass(cls):
        # print("tearDownClass")
        pass

    def _get_combination(self, r: int):
        """
        bitパターンのすべてを生成
        (Gosper's Hackと同じ機能)
        """
        for bit_tuple in itertools.combinations(NOT_CENTER_POS, r):
            # 中心の4マスを含むビットリスト
            bit_with_center_list = list(bit_tuple) + CENTER_POS
            # ビット化
            result = 0
            for bit in bit_with_center_list:
                result |= (1<<bit)
            
            yield result

    """
    [テスト]
    1. 件数テスト(※時間がかかるため60C(1-5)と60C(56-60)
    2. 既存の60Cgenerationを求めるものと計算結果が同じか
    """
    def test_result_count(self):
        # 1. 件数テスト(※時間がかかるため60C(1-5)と60C(56-60)
        for r in [1,2,3,4,5,56,57,58,59,60]:
            result = len(list(get_60_c_r_by_gosper_hack_with_state_bit(r)))
            exp = self._60_c_r[str(r)]
            self.assertEqual(exp, result)
    
    def test_compare_new_old(self):
        # 2. 既存の60Cgenerationを求めるものと計算結果が同じか(1-5)と60C(56-60)
        for r in [1,2,3,4,5,56,57,58,59,60]:
            new_result = list(get_60_c_r_by_gosper_hack_with_state_bit(r))
            old_result = list(self._get_combination(r))
            new_result.sort()
            old_result.sort()
            self.assertEqual(new_result, old_result)
