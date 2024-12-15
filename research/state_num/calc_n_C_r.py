"""
nCrを計算するn_C_r.csvを出力する
"""

import csv
from math import comb

def calc_n_c_r():
    rows = []
    header = ["n", "r", "結果", "10の何乗か"]
    rows.append(header)

    for r in range(64+1):
        n = 64  # 固定
        pattern_num = comb(n, r)  # 64Cr

        # 10の何乗かを求める
        ten = len(str(pattern_num)) - 1

        rows.append([n, r, pattern_num, ten])
    
    # CSV出力
    with open("n_C_r.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


if __name__ == "__main__":
    calc_n_c_r()
