"""
「石を置く組み合わせをnpyファイルで保存する」処理を方法によって速度を比較する
1. シングルプロセス
2. マルチプロセス
3. njit(parallel=False)
4. njit(parallel=True)
5. judge_alone前までvectorize
   後は(分岐があるので)jit
6. rayでコンテナによるマルチプロセス(分散処理)

"""
from itertools import combinations
import csv
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import multiprocessing
import numpy as np
import tempfile
import multiprocessing

from env_v2.common.symmetory import normalization
from common.dt_utils import sec_to_str
from common.numerical_utils import get_with_jp_unit



# 中心4マスの位置
CENTER_POS = [27, 28, 35, 36]
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


def save_stone_pos(generation: int) -> int:
    """
    1. シングルプロセスで石を置く組み合わせをnpyファイルで保存する

    作成ファイル: 
        1. 計測時間: 1_single_process.csv
        2. npyファイル: 一時ディレクトリ

    returns:
      calc_time: 計測時間
      file_path: 計測時間のファイルパス
    """
    start_time = time.time()

    stone_pos_list = []
    for stone_pos in combinations(NOT_CENTER_POS, generation):

        # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
        stone_pos_with_center = list(stone_pos) + CENTER_POS
        # 1) stone_pos_with_center をビットマスク化
        mask_of_stone_pos_with_center = 0
        for pos in stone_pos_with_center:
            mask_of_stone_pos_with_center |= (1 << pos)
        
        if _judge_alone_stone(mask_of_stone_pos_with_center):
            continue

        stone_pos_list.append(stone_pos_with_center)
    
    stone_pos_ndarray = np.array(stone_pos_list)

    # save
    file_name = "1_single_process.npy"
    with tempfile.TemporaryDirectory() as tmpdir:
        # 一時ディレクトリ
        file_path = tmpdir + "/" + file_name
        np.save(file_path, stone_pos_ndarray)
    
    base_folder = os.path.dirname(__file__)
    file_name = "1_single_process.csv"
    file_path = base_folder + f"/{generation}/" + file_name
    
    return time.time() - start_time, file_path


# def _save_stone_pos_by_multiprocessing(generation: int, save_dir: str) -> None:
#     """
#     2. マルチプロセス(multiprocessing)で石を置く組み合わせをnpyファイルで保存する
#     """
#     chunk_list = []
#     for stone_pos in combinations(NOT_CENTER_POS, generation):

#     with multiprocessing.Pool() as pool:
#         results = pool.imap(
            
#         )

# def _multi_func():
#     pass
# def _get_yield_array(chunk_size=10000):
#     i = 0
#     results = []
#     for comb in combinations(NOTE_CE)
    
    

def _save_stone_pos_by_njit(generation: int, is_parallel: bool, save_dir: str) -> None:
    """
    njitで石を置く組み合わせをnpyファイルで保存する

    args:
      is_parallel: 配列要素を独立して並列に処理できる場合にTrueにして高速化する
    """
    pass

def _judge_alone_stone(board: int) -> bool:
    """
    孤立石かどうかを判定する

    args:
      board: 黒石または白石
    """
    # 境界処理用マスク(両端の列マスク)
    mask_without_a_col = 0x7f7f7f7f7f7f7f7f  # A列(左端)を除くマスク
    mask_without_h_col = 0xfefefefefefefefe  # H列(右端)を除くマスク

    # ボードの最下位ビットの石のから順にチェック
    check_board = board
    while check_board != 0:
        # すべての石をチェック(=0)するまでループ

        """
        A & (-A): 最下位の立っているビットを抽出

        -A: 2の補数: プログラムにおいて「-A=~A+1」
          ex) -ob1010=0b0101 + 0b0001
        A&(-A): 最下位の立っているビットを抽出することができるテクニック
          ex) a = 0b1010 -> 最下位ビットを抽出すると0b0010
              a & (-a)
              =0b1010 & (0b0101+0b0001)
              =0b1010 & 0b0010
              =0b0010
        """
        position = check_board & (-check_board)  # 最下位の立っているビットを抽出(処理対象のマス)
        """
        最下位のビットを取り除く

        positionは最下位の立っているビットのためボードと排他的論理和を取ることで最下位のビットは1と1の関係性のため
        最下位のビットを0に更新できる

        XOR(排他的論理和)
        a b c
        0 0 0
        0 1 1
        1 0 1
        1 1 0
        """
        check_board ^= position  # 最下位のビットを取り除く(最下位のビットを0にしてboardを更新)

        # 各8方向に石があるかチェック
        right = (position >> 1) & board & mask_without_a_col  # 元のボードの処理対象のマスの右のマスに石があるか かつ 処理対象のマスが右端ではないか
        left = (position << 1) & board & mask_without_h_col  # 元のボードの処理対象のマスの左のマスに石があるか かつ 処理対象マスが左端ではないか
        up = (position << 8)  & board  # 一番上のボートの場合元のボードでmaskする際にoutになるので左端、右端のようにmaskする必要がない
        down = (position >> 8) & board 
        left_up = (position << 9) & board & mask_without_h_col  # 元のボードの処理対象のマスの左上に石があるか かつ 処理対象のマスが左端ではないか
        left_down = (position >> 7) & board & mask_without_h_col  # 元のボードの処理対象のマスの左下に石があるか かつ 処理対象のマスが左端ではないか
        right_up = (position << 7) & board & mask_without_a_col  # 元のボードの処理対象のマスの右上に石があるか かつ 処理対象マスが右端ではないか
        right_down = (position >> 9) & board & mask_without_a_col  # 元のボードの処理対象のマスの右下に石があるか かつ 処理対象マスが右端ではないか

        # 各8方向に石が1つもなければ孤立石と判定
        if (right | left | up | down | left_up | left_down | right_up | right_down) == 0:
            return True 

    # すべての石があるマスを調べて1つも孤立石がない場合False
    return False

if __name__ == "__main__":
    generation = 2

    # exec
    calc_time, file_path = save_stone_pos(generation)  # # シングルプロセス

    # 計測結果
    calc_time = sec_to_str(calc_time)
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows([["計測結果"], [calc_time]])