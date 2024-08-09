"""
2024/08/08 リファクタリング + Cython
"""
"""
分散処理でバッチごとに処理
世代ごとの状態数を算出する
"""
import csv
import time
import ray
import msgpack
import glob
import os

from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER,\
    BATCH_NUM
from env_v2.anality.ray_calc_next_states_cython import ray_calc_next_states_cython

PLAYER_BLACK = 0
PLAYER_WHITE = 1
PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)

 
def run(generation: int):
    """
    Args:
        generation (int): 世代
  
    処理
        1. 1世代前の状態ファイルを読み取る
        2. 状態の算出
        3. 状態ファイル作成
        4. 分析ファイル作成
    """
    print(f"------------算出する世代:{generation}------------")
    
    start_time = time.time()
    if generation == 0:
        next_states, cut_num = _calc_next_states_ini(generation)
    else:
        # 1世代前の状態ファイルを読み取る
        states = _get_state_file(generation-1)
        # 2. 状態の算出
        next_states, cut_num = _calc_next_states(generation, states)
    calc_time = time.time() - start_time
    
    # 3. 状態ファイル作成
    _write_state_file(generation, next_states)
    
    # 4. 分析ファイル作成
    _write_anality_file(generation, len(next_states), cut_num, calc_time)
    
def _get_state_file(generation: int) -> list[str]:
    """
    returns:
        datas: 状態のリスト
    """
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = TMP_REPORT_FOLDER + file_name

    with open(file_path, "r") as f:
        reader = csv.reader(f)
        datas = [row[0] for row in reader]  # 1行当たり1つの項目のみ

    return datas

def _calc_next_states_ini(generation: int) -> tuple:
    """世代0の状態を算出する

    Args:
        generation (int): 世代

    Returns:
        states: 0世代の状態
        cut_sym: 0世代の対称性によるカット数
    """
    ini_black_board = 0x0000000810000000
    ini_white_board = 0x0000001008000000
    ini_player_id = PLAYER_BLACK
    
    datas = [f"{ini_black_board}_{ini_white_board}_{ini_player_id}"]
    
    return datas, 0
    
def _calc_next_states(generation: int, states: list[str]) -> tuple:
    """次の状態を算出する

    Args:
        generation: 算出する世代
        states (list[str]): 1世代前の状態

    Returns:
        next_states: 次の状態
        cut_sym: 対称性によりカットした数
    """
    ray.init()
    calc_state_num = len(states)  # 計算する1つ前の世代のノード数
    proc_num = calc_state_num // BATCH_NUM + 1  # 計算するプロセス数
    
    print(f"算出するノード数: {calc_state_num}")
    
    # Queueにタスクをすべて投入する
    ray_ids = []
    for i in range(1, proc_num):
        ray_ids.append(_ray_calc_next_states.remote(states[0: BATCH_NUM], i*BATCH_NUM, generation))
        del states[:BATCH_NUM]
    if len(states) != 0:
        ray_ids.append(_ray_calc_next_states.remote(states, calc_state_num, generation))
    del states
    print("非同期ですべての次の状態数を算出する処理を投下済み")
    
     # 2. すべての次の状態を算出できるまで待つ
    ray.get(ray_ids)
    ray.shutdown()
    
    print("全ての状態の算出終了!!!")
    
        # ファイルを一括取得する
    files = glob.glob(f"env_v2/anality/report/tmp/{generation}/*")
    state_num = 0
    cut_num = 0  # 対称性でカットした回数
    next_states_set = set()
    for file in files:
        with open(file, "rb") as f:
            deserialized = msgpack.load(f, raw=False)
            state_num += len(deserialized[0])
            cut_num += deserialized[1]
            next_states_set |= set(deserialized[0])
    
    cut_num += state_num - len(next_states_set)
    return next_states_set, cut_num

@ray.remote(max_retries=-1)
def _ray_calc_next_states(states: list[str], index, generation) -> set[str]:
    """
    次の状態数を算出する
    """
    ray_calc_next_states_cython(states, index, generation)

def _write_state_file(generation: int, next_states: list[str]) -> None:
    """状態ファイル作成
    
    """
    start_time = time.time()
    
    file_path = TMP_REPORT_FOLDER + STATE_FILE_NAME.replace("GENERATION", str(generation))
    rows = [[next_state] for next_state in next_states]
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    
    print(f"状態ファイル作成時間: {time.time()-start_time}")
    
    
def _write_anality_file(generation: int, state_num: int, cut_num: int, calc_time: int) -> None:
    """分析ファイル作成
    
    """
    HEADERS = ["状態数", "計算時間", "対称性カット数"]
    
    file_path = TMP_REPORT_FOLDER + ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerow([state_num, calc_time, cut_num])
    