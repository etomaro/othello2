import time 
import os
import csv
from datetime import datetime 
from zoneinfo import ZoneInfo

from common.dt_utils import sec_to_str
from common.n_C_r import json_utils
from common.numerical_utils import get_powers_of_ten, get_with_jp_unit


def calc(generation: int) -> int:
    """
    世代ごとの雑な推定最大状態数を求める

    1. 中心を除いた石のおけるパターン数を算出(=中心を除いた60マスの内(黒と白のおける石の数)-4(中心のマス)のパターン数)
    2. 石の数より黒と白のおける石のパターンを求める
    3. 2で求めたパターンごとに黒と白のマスのとり方を求める
    4. 1で求めた数 * 3で求めた数より世代の雑な推定最大状態数を求める

    args:
      generation: 世代
    """
    stone_num = generation + 4  # 石の数
    stone_num_without_center = generation  # 中心マス以外の石の数

    # 1. 中心を除いた石のおけるパターン数を算出(=中心を除いた60マスの内(黒と白のおける石の数)-4(中心のマス)のパターン数)
    stone_pos_patter = json_utils.read_json_n_c_r(60)[str(stone_num_without_center)]

    # 2. 石の数より黒と白のおける石のパターンを求める
    stone_num_pattern = []
    for black_stone_num in range(stone_num+1):
        # 合計石数の半数を超えた場合ループ終了
        if black_stone_num > (stone_num/2):
            break
    
        white_stone_num = stone_num - black_stone_num
        stone_num_pattern.append((black_stone_num, white_stone_num))
    
    # 3. 2で求めたパターンごとに黒と白のマスのとり方を求める
    black_white_pattern = {}
    for black_num, white_num in stone_num_pattern:
        min_num = min(black_num, white_num)
        # (stone_num)C(min_num)
        black_white_pattern[(black_num, white_num)] = json_utils.read_json_n_c_r(stone_num)[str(min_num)]
    
    # 4. 1で求めた数 * 3で求めた数より世代の雑な推定最大状態数を求める
    estimated_num = 0
    for black_white_num, value in black_white_pattern.items():
        black_num, white_num = black_white_num 
        if black_num == white_num:
            estimated_num += (stone_pos_patter*value) 
        else:
            estimated_num += (stone_pos_patter*value)*2

    return estimated_num

if __name__ == "__main__":
    header = ["世代", "推定状態数", "推定状態数(単位)", "10の何乗か", "計測時間"]
    datas = {}  # {generation: {estimated_"num: N, calc_time: M}}
    for generation in range(1, 60+1):
        print(f"世代: {generation} calc start.")
        
        start_time = time.time()

        # 計算
        estimated_num = calc(generation)

        calc_time_sec = int(time.time() - start_time)
        calc_time_str = sec_to_str(calc_time_sec)

        datas[generation] = {"estimated_num": estimated_num, "calc_time": calc_time_str}
        
        print(f"世代: {generation} calc end.")
    
    # CSV出力
    base_folder = os.path.dirname(__file__)
    file_path = base_folder + "/" + f"estimated_state_max_rough_num.csv"
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        rows = [header]
        for generation, data in datas.items():
            rows.append(
                [
                    str(generation), data["estimated_num"], get_with_jp_unit(data["estimated_num"]),
                    get_powers_of_ten(data["estimated_num"]), data["calc_time"]
                ]
            )
        writer.writerows(rows)
