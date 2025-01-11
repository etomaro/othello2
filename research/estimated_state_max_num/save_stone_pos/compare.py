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
import shutil

from env_v2.common.symmetory import normalization
from common.dt_utils import sec_to_str
from common.numerical_utils import get_with_jp_unit
from common.n_C_r.json_utils import read_json_n_c_r



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

    # {generation}_npyフォルダ配下のファイルをすべて削除する
    base_folder = os.path.dirname(__file__) + "/" f"{generation}/1_npy"
    if os.path.isdir(base_folder):
        shutil.rmtree(base_folder)
    else:
        os.makedirs(base_folder)

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
    pattern_num = len(result)

    # save
    file_name = "1_single_process.npy"
    with tempfile.TemporaryDirectory() as tmpdir:
        # 一時ディレクトリ
        file_path = tmpdir + "/" + file_name
        np.save(file_path, result_ndarray)
    
    base_folder = os.path.dirname(__file__)
    file_name = "1_single_process.csv"
    file_path = base_folder + f"/{generation}/" + file_name
    
    return time.time() - start_time, file_path, pattern_num


# ------------------------2. マルチプロセス(multiprocessing)------------------------    
def save_stone_pos_by_multiprocessing(generation: int) -> int:
    """
    2. マルチプロセス(multiprocessing)で石を置く組み合わせをnpyファイルで保存する
    バッチごとにnpyファイルを作成する

    ※ メインプロセスで60Cgenerationの配列を作成してworkerに渡すとコピーされ倍のメモリを使用するためworkerごとに作成する

    [メインプロセス]
    {generation}_npyフォルダ配下のファイルをすべて削除する
    コア数(multiprocessing.cpu_count()=16)個のworkerを動かす
      1. 1worker当たりのタスク量を求める
      2. 「1」の値をコア数で均等に処理できるようにworkerごとの範囲を指定する

    [各worker]
    1. 60Cgenerationの遅延リストを作成する
    2. workerに指定された範囲の「1」の範囲をiterateする
    3. 各workerが保持できる最大数を超えた場合npyファイルとして保存する
       「各workerが保持できる最大数の求め方」
         ・a = [0xffffffffffffffff] * 4000000000  # 40億のリスト
            -> 32GBメモリ、2GBのスワップ

            multiprocessをする場合の検討
            40億を1/4をつまり75%をMax使用できるとして
            np.array()でほぼ倍になるため半分の20億
            ボードの状態は2つ保持するため半分の10億の状態
            multiprocessing.cpu_count()=16のため16個の並列処理が動かせる。そのため1podあたり6250万個
        
        保存path
          各workerのprocess_idをフォルダベースとしてworker内の処理単位ごとにファイルを作成する
          base_folder/{generation}/2_npy/{worker_id}/{proc_id}.npy
    """
    start_time = time.time()

    # {generation}_npyフォルダ配下のファイルをすべて削除する
    base_folder = os.path.dirname(__file__) + "/" f"{generation}/2_npy"
    if os.path.isdir(base_folder):
        shutil.rmtree(base_folder)
    else:
        os.makedirs(base_folder)

    core_num = multiprocessing.cpu_count()  # コア数

    # 1. 1worker当たりのタスク量を求める
    pos_total_num = read_json_n_c_r(60)[str(generation)]  # 60Cgenerationの件数を取得する
    work_num_by_worker = int(pos_total_num/core_num) + 1

    # 2. 「1」の値をコア数で均等に処理できるようにworkerごとの範囲を指定する.(generation, save_folder, start_idx, end_idx)
    args = []
    start_idx = 0
    end_idx = work_num_by_worker
    for i in range(core_num):
        # iをworker_idとする
        save_folder = base_folder + "/" + f"{str(i)}" + "/"
        args.append((generation, save_folder, start_idx, end_idx))
        start_idx = end_idx 
        end_idx += work_num_by_worker
    
    print(f"pos_total_num={pos_total_num}")
    print(f"work_num_by_worker={work_num_by_worker}")
    for i in args:
        print(f"start_idx: {i[2]}. end_idx: {i[3]}")
    
    with multiprocessing.Pool(core_num) as pool:
        # バッチごとに処理する
        # workerに渡す配列が大きすぎるため(copyが起きる)OOMが発生しやすくなる
        # 生成をworkerで行うようにしてOOMを避ける
        pattern_nums = pool.map(_wrapper_process_by_worker, args)

    pattern_num = sum(pattern_nums)

    base_folder = os.path.dirname(__file__)
    file_name = "2_multi_process.csv"
    file_path = base_folder + f"/{generation}/" + file_name
    
    return time.time() - start_time, file_path, pattern_num

def _get_pos_by_range(generation: int, start_idx: int, end_idx: int):
    """
    指定した範囲で選択マスをyieldする

    args
      batch_size: デフォルト1000万
    """
    not_center_pos = [
        0, 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14, 15,
        16, 17, 18, 19, 20, 21, 22, 23,
        24, 25, 26, 29, 30, 31,
        32, 33, 34, 37, 38, 39,
        40, 41, 42, 43, 44, 45, 46, 47,
        48, 49, 50, 51, 52, 53, 54, 55,
        56, 57, 58, 59, 60, 61, 62, 63
    ]
    all_combos = itertools.combinations(not_center_pos, generation)
    return list(itertools.islice(all_combos, start_idx, end_idx))

def _process_by_worker(generation: int, save_folder: str, start_idx: int, end_idx: int) -> int:
    """
    worker当たりのタスク
    1. 配置可能マス取得
    2. ビットマスク化
    3. 孤立石除外
    4. npyファイル作成

    args:
      generation: 世代
      save_folder: 保存フォルダのパス
      start_idx: 選択可能マスの範囲開始index
      end_idx: 選択可能マスの範囲終了index
    returns:
      pattern_num_by_worker: workerで計算したパターン数
    """
    pattern_num_by_worker = 0

    # OOMを気にしながら状態保存をする単位
    batch_num = 62500000  # 6250万

    # batch_numごとに引数で指定された範囲を処理する
    proc_id = 0
    for _start_idx in range(start_idx, end_idx, batch_num):
        if (_start_idx + batch_num) > end_idx:
            _end_idx = end_idx
        else:
            _end_idx = _start_idx + batch_num
        # 処理する選択可能マスのパターンを取得する
        stone_pos_list = _get_pos_by_range(generation, _start_idx, _end_idx)

        estimated_boards = []
        for stone_pos in stone_pos_list:
            # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
            stone_pos_with_center = list(stone_pos) + CENTER_POS
            # 1) stone_pos_with_center をビットマスク化
            mask_of_stone_pos_with_center = 0
            for pos in stone_pos_with_center:
                mask_of_stone_pos_with_center |= (1 << pos)
            
            if _judge_alone_stone(mask_of_stone_pos_with_center):
                continue

            estimated_boards.append(stone_pos_with_center)
        
        del stone_pos_list
        
        # 状態を保存する 
        file_path = save_folder + f"{proc_id}.npy"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # ディレクトリが存在している場合もエラーが出ないようにディレクトリを作成
        estimated_boards_ndarray = np.array(estimated_boards)
        np.save(file_path, estimated_boards_ndarray)

        proc_id += 1
        pattern_num_by_worker += len(estimated_boards)
        del estimated_boards
        del estimated_boards_ndarray
    
    return pattern_num_by_worker

def _wrapper_process_by_worker(args) -> int:
    pattern_num_by_worker = _process_by_worker(*args)

    return pattern_num_by_worker

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
    
    for generation in range(1, 2):
        # debug用出力
        now_dt = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
        now_str = f"{now_dt.year}/{now_dt.month}/{now_dt.day} {now_dt.hour}:{now_dt.minute}"
        print(f"世代={generation} start. {now_str}")
        
        # exec
        # calc_time, file_path, pattern_num = save_stone_pos(generation)  # 1. シングルプロセス
        calc_time, file_path, pattern_num = save_stone_pos_by_multiprocessing(generation)  # 2. マルチプロセス

        # 計測結果
        calc_time = sec_to_str(calc_time)
        now_dt = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
        now_str = f"{now_dt.year}/{now_dt.month}/{now_dt.day} {now_dt.hour}:{now_dt.minute}"

        with open(file_path, "w") as f:
            f.seek(0)
            writer = csv.writer(f)
            writer.writerows([["計測結果", "パターン数", "実行日時"], [calc_time, pattern_num, now_str]])
