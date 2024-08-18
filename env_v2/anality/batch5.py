"""
2024/08/14 numba+numpyでメモリ節約、高速化

分散処理でバッチごとに処理
世代ごとの状態数を算出する
"""
import csv
import time
import ray
import msgpack
import glob
import os
import numpy as np
from numpy import int64

from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER,\
    BATCH_NUM
from env_v2.env_by_numpy import get_initial_board, get_actions, step_parallel
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.policy.negamax_player import NegaMaxPlayer
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate
from env_v2.symmetory.symmetory import get_symmetorys, get_symmetory_for_anality_batch

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
        next_states, cut_num = _calc_next_states_ini()
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
    
def _get_state_file(generation: int) -> np.ndarray:
    """
    returns:
        datas(numpy.ndarray) 状態の2重配列
    """
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = TMP_REPORT_FOLDER + file_name

    states = np.loadtxt(file_path, delimiter=',', dtype=np.uint64)
    # 1次元の場合2次元に変換
    if states.ndim == 1:
        states = states.reshape(1, -1)

    return states

def _calc_next_states_ini() -> tuple:
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
    
    return [[ini_black_board, ini_white_board, ini_player_id]], 0
    
def _calc_next_states(generation: int, states: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """次の状態を算出する
    Args:
        generation: 算出する世代
        states (numpy.ndarray): 1世代前の状態

    Returns:
        next_states(2重リスト): 次の状態
        cut_sym(1次元リスト): 対称性によりカットした数
    """
    ray.init()
    calc_state_num = states.shape[0]  # 計算する1つ前の世代のノード数
    proc_num = calc_state_num // BATCH_NUM + 1  # 計算するプロセス数
    
    print(f"算出するノード数: {calc_state_num}")
    
    # Queueにタスクをすべて投入する
    ray_ids = []
    for i in range(1, proc_num):
        ray_ids.append(_ray_calc_next_states.remote(states[0: BATCH_NUM][:], i*BATCH_NUM, generation))
        # TODO: np.deleteは新しいオブジェクトを生成するためメモリ効率悪い
        states =  np.delete(states, slice(0,BATCH_NUM), axis=0)
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
    next_state_num = 0
    cut_num = 0  # 対称性でカットした回数
    next_states_set = set() 
    for file in files:
        with open(file, "rb") as f:
            deserialized = msgpack.load(f, raw=False)
            next_state_num += len(deserialized[0])
            cut_num += deserialized[1]
            next_states_set |= set([tuple(state) for state in deserialized[0]])
    
    # print("next_states_set: ", next_states_set)
    cut_num += next_state_num - len(next_states_set)
    return next_states_set, cut_num

@ray.remote(max_retries=-1)
def _ray_calc_next_states(states: np.ndarray, index, generation):
    """
    次の状態数を算出する
    
    1. ゲームが終了している場合除外する
    2. アクション可能ハンドを取得する
    3. アクションを行う(対称性も使用)
    4. 同じ状態をカット
    5. 次の状態のリストに追加する
    """
    print("_ray_calc_next_states called: ", index)
    # 1. ゲームが終了している場合除外する
    # print("states.shape: ", states.shape)
    states = states[states[:, 2] != PLAYER_UNKNOW]
    # print("states: ", states)
    # 2. アクション可能ハンドを取得する
    actions = get_actions(states.tolist())
    # print("actions: ", actions)
    # 3. アクションを行う(対称性も使用)
    dummy = np.zeros(3, dtype=np.uint64)
    # print("dummy: ", dummy)
    actions = np.array(actions, dtype=np.uint64)
    next_states = step_parallel(actions, dummy)
    # print("next_states: ", next_states)
    # print("next_states.shape: ", next_states.shape)
    # 4. 同じ状態をカット
    num_next_states = next_states.shape[0]
    next_states_unique = np.unique(next_states, axis=0)  # 次のstateで同じ状態または対称性により同じ状態をカット
    cut_num = num_next_states - next_states_unique.shape[0]
    
    # メモリにデータを登録しないようにstorageに登録する
    # print("next_states_unique: ", next_states_unique)
    # print("next_states_unique.tolist(): ", next_states_unique.tolist())
    serialized = msgpack.packb((next_states_unique.tolist(), cut_num))
    folder_path = TMP_REPORT_FOLDER + str(generation)
    file_path = folder_path + f"/{index}.bin"
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    with open(file_path, "wb") as f:
        f.write(serialized)
        
    print(f"index: {index}. next state calc done")

def _write_state_file(generation: int, next_states: list[str]) -> None:
    """状態ファイル作成
    
    """
    start_time = time.time()
    
    file_path = TMP_REPORT_FOLDER + STATE_FILE_NAME.replace("GENERATION", str(generation))
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(next_states)
    
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
    