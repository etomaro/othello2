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
import itertools
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

# ------------------------1. シングルプロセス------------------------
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

    result = []
    for stone_pos in combinations(NOT_CENTER_POS, generation):

        # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
        stone_pos_with_center = list(stone_pos) + CENTER_POS
        # 1) stone_pos_with_center をビットマスク化
        mask_of_stone_pos_with_center = 0
        for pos in stone_pos_with_center:
            mask_of_stone_pos_with_center |= (1 << pos)
        
        if _judge_alone_stone(mask_of_stone_pos_with_center):
            continue

        result.append(stone_pos_with_center)
    
    result_ndarray = np.array(result)

    # save
    file_name = "1_single_process.npy"
    with tempfile.TemporaryDirectory() as tmpdir:
        # 一時ディレクトリ
        file_path = tmpdir + "/" + file_name
        np.save(file_path, result_ndarray)
    
    base_folder = os.path.dirname(__file__)
    file_name = "1_single_process.csv"
    file_path = base_folder + f"/{generation}/" + file_name
    
    return time.time() - start_time, file_path


# ------------------------2. マルチプロセス(multiprocessing)------------------------    
def save_stone_pos_by_multiprocessing(generation: int) -> int:
    """
    2. マルチプロセス(multiprocessing)で石を置く組み合わせをnpyファイルで保存する
    
    バッチごとにnpyファイルを作成する
    """
    start_time = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        with multiprocessing.Pool() as pool:
            # バッチごとに処理する
            pool.imap(_wrapper_mult_fuc, _chunked_combinations(tmpdir))
    
    base_folder = os.path.dirname(__file__)
    file_name = "2_multi_process.csv"
    file_path = base_folder + f"/{generation}/" + file_name
    
    return time.time() - start_time, file_path

def _chunked_combinations(save_dir: str, batch_size=10000000):
    """
    バッチごとにyieldする

    args
      batch_size: デフォルト1000万
    """
    combo_iter = itertools.combinations(NOT_CENTER_POS, generation)
    idx = 0
    while True:
        # isliceでcombo_iterからbatch_size分だけ取り出し
        chunk = list(itertools.islice(combo_iter, batch_size))
        save_path = save_dir + "/" + f"{idx}"
        if not chunk:
            break
        yield chunk, save_path

        idx += 1

def _multi_fnc(stone_pos_list: list, save_path: str):
    """
    並列用関数
    1. 配置可能マス取得
    2. ビットマスク化
    3. 孤立石除外
    4. npyファイル作成
    """
    result = []
    for stone_pos in stone_pos_list:
        # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
        stone_pos_with_center = list(stone_pos) + CENTER_POS
        # 1) stone_pos_with_center をビットマスク化
        mask_of_stone_pos_with_center = 0
        for pos in stone_pos_with_center:
            mask_of_stone_pos_with_center |= (1 << pos)
        
        if _judge_alone_stone(mask_of_stone_pos_with_center):
            continue

        result.append(stone_pos_with_center)
    
    result_ndarray = np.array(result)
    np.save(save_path, result_ndarray) 

def _wrapper_mult_fuc(args):
    _multi_fnc(*args)

# -----------------3. njit------------------
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
    
    for generation in range(5, 11):
        # debug用出力
        now_dt = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
        now_str = f"{now_dt.year}/{now_dt.month}/{now_dt.day} {now_dt.hour}:{now_dt.minute}"
        print(f"世代={generation} start. {now_str}")
        
        # exec
        calc_time, file_path = save_stone_pos_by_multiprocessing(generation)  # 2. マルチプロセス

        # 計測結果
        calc_time = sec_to_str(calc_time)
        now_dt = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
        now_str = f"{now_dt.year}/{now_dt.month}/{now_dt.day} {now_dt.hour}:{now_dt.minute}"

        with open(file_path, "w") as f:
            f.seek(0)
            writer = csv.writer(f)
            writer.writerows([["計測結果", "実行日時"], [calc_time, now_str]])
