"""
マスの選択の際に「除外された場合」最終的に除外された計算数を世代ごとに求める
"""
from itertools import combinations
import csv
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import multiprocessing
import math

from env_v2.common.symmetory import normalization
from common.dt_utils import sec_to_str
from common.numerical_utils import get_with_jp_unit


def calc(generation: int):
    # 2^(g+4)/(g+4)!
    return 2**(generation+4)

def main() -> None:
    """
    
    出力レポート
      path: report_remove_num.csv
    """
    
    base_folder = os.path.dirname(__file__)
    file_path = base_folder + "/" + "report_remove_num.csv"


    with open(file_path, "w") as f:
        writer = csv.writer(f)
        header = ["世代", "最終的に除外される計算数"]
        rows = [header]
        for generation in range(1, 60+1):
            remove_num = calc(generation)
            remove_num_str = get_with_jp_unit(remove_num) + "k"
            rows.append([str(generation), remove_num_str])
        
        writer.writerows(rows)

if __name__ == "__main__":
    main()
