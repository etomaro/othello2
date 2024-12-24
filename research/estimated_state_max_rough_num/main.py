import time 
import os
import csv
from datetime import datetime 
from zoneinfo import ZoneInfo

from common.dt_utils import sec_to_str



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

if __name__ == "__main__":
    header = ["世代", "推定状態数", "計測時間"]
    datas = {}  # {generation: {estimated_num: N, calc_time: M}}
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
            rows.append([str(generation), data["estimated_num"], data["calc_time"]])
        writer.writerows(rows)