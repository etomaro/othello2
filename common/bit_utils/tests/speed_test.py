import unittest
import itertools
import time
import os
import csv

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


def _get_combination(r: int):
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

def test_speed(r: int):
    # 3. 既存の60Cgenerationを求めるものとの速度調査(60C10=750億)
    # new
    new_start_time = time.time()
    for _ in get_60_c_r_by_gosper_hack_with_state_bit(r):
        pass  # ループするのみ
    new_calc_time = time.time() - new_start_time 

    print("new calc done.")

    # old
    old_start_time = time.time()
    for _ in _get_combination(r):
        pass  # ループするのみ
    old_calc_time = time.time() - old_start_time
    
    print("old calc done.")

    # debug出力
    print(f"new calc time: {int(new_calc_time)}: {sec_to_str(new_calc_time)}")
    print(f"old calc time: {int(old_calc_time)}: {sec_to_str(old_calc_time)}")

    folder_name = os.path.dirname(__file__)
    # file_name = f"speed_test_60_c_{r}.csv"
    file_name = f"speed_test_60_c_{r}_pypy.csv"  # pypyで実行
    file_path = folder_name + "/" + file_name
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        datas = [
            ["項目", "計算時間", "計算時間(単位)"],
            [
                "古", int(old_calc_time), sec_to_str(old_calc_time)
            ],
            [
                "新", int(new_calc_time), sec_to_str(new_calc_time)
            ],
        ]
        writer.writerows(datas)

if __name__ == "__main__":
    # pythonかpypy3で実行するか考え、ファイル名を適切に変更する
    r = 8
    test_speed(r)
