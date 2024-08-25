"""
2024/08/25 numpy形式でファイルを保存

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
    BATCH_NUM, STATE_FILE_NAME2
from env_v2.env_by_numpy import get_initial_board, get_actions, step_parallel
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.policy.negamax_player import NegaMaxPlayer
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate
from env_v2.symmetory.symmetory import get_symmetorys, get_symmetory_for_anality_batch
from memory_profiler import profile


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
    _write_anality_file(generation, next_states.shape[0], cut_num, calc_time)
    
def _get_state_file(generation: int) -> np.ndarray:
    """
    returns:
        datas(numpy.ndarray) 状態の2重配列
    """
    file_name = STATE_FILE_NAME2.replace("GENERATION", str(generation))
    file_path = TMP_REPORT_FOLDER + file_name

    states = np.load(file_path)

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
    
    return np.array([[ini_black_board, ini_white_board, ini_player_id]],dtype=np.uint64), 0

def _calc_next_states(generation: int, states: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """次の状態を算出する
    Args:
        generation: 算出する世代
        states (numpy.ndarray): 1世代前の状態

    Returns:
        next_states(2重リスト): 次の状態
        cut_sym(1次元リスト): 対称性によりカットした数
    """
    # 1. ゲームが終了している場合除外する
    states = states[states[:, 2] != PLAYER_UNKNOW]
    
    ray.init()
    calc_state_num = states.shape[0]  # 計算する1つ前の世代のノード数
    proc_num = calc_state_num // BATCH_NUM + 1  # 計算するプロセス数
    
    print(f"算出するノード数: {calc_state_num}")
    
    # Queueにタスクをすべて投入する
    ray_ids = []
    for i in range(1, proc_num):
        # putを使うことでメモリ節約になるらしい
        # https://yuiga.dev/blog/posts/rayremote%E3%81%8C%E3%83%A1%E3%83%A2%E3%83%AA%E3%82%92%E5%A4%A7%E9%87%8F%E3%81%AB%E9%A3%9F%E3%81%86%E6%99%82%E3%81%AFray.put%E3%82%92%E4%BD%BF%E3%81%8A%E3%81%86/
        ray_id = ray.put(states[0: BATCH_NUM][:])
        ray_ids.append(_ray_calc_next_states.remote(ray_id, i*BATCH_NUM, generation))
        # TODO: np.deleteは新しいオブジェクトを生成するためメモリ効率悪い
        states =  np.delete(states, slice(0,BATCH_NUM), axis=0)
    if len(states) != 0:
        ray_id = ray.put(states[0: BATCH_NUM][:])
        ray_ids.append(_ray_calc_next_states.remote(ray_id, calc_state_num, generation))
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
    next_states = None
    for file in files:
        # ファイルパスから拡張子を除いたファイル名を取得
        file_name = os.path.splitext(os.path.basename(file))[0]
        _, tmp_cut_num = file_name.split("_")
        cut_num+=int(tmp_cut_num)
        # ファイル読み込み
        tmp_next_states = np.load(file)
        next_state_num += tmp_next_states.shape[0]
        if next_states is None:
            next_states = tmp_next_states
        else:
            next_states = np.concatenate([next_states, tmp_next_states])
    
    # print("next_states_set: ", next_states_set)
    cut_num += next_state_num - next_states.shape[0]
    next_states = np.unique(next_states, axis=0)  # 次のstateで同じ状態または対称性により同じ状態をカット
    return next_states, cut_num

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
    # 2. アクション可能ハンドを取得する
    # TODO: メモリ節約のためnumpy化したい
    actions = get_actions(states)
    # print("actions: ", actions)
    # 3. アクションを行う(対称性も使用)
    dummy = np.zeros(3, dtype=np.uint64)
    # print("dummy: ", dummy)
    next_states = step_parallel(actions, dummy)
    
    # dubug
    # print("----step調査----")
    # for state in next_states.tolist():
    #     if bin(state[0]).count("1") + bin(state[1]).count("1") !=11:
    #         print(state)
    # time.sleep(10)
    
    
    # 4. 同じ状態をカット
    num_next_states = next_states.shape[0]
    next_states = np.unique(next_states, axis=0)  # 次のstateで同じ状態または対称性により同じ状態をカット
    cut_num = num_next_states - next_states.shape[0]
    
    # メモリにデータを登録しないようにstorageに登録する
    # print("next_states_unique: ", next_states_unique)
    # print("next_states_unique.tolist(): ", next_states_unique.tolist())
    folder_path = TMP_REPORT_FOLDER + str(generation)
    file_path = folder_path + f"/{index}_{cut_num}.npy"  # {index}_{cut_num}
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    np.save(file_path, next_states)
        
    print(f"index: {index}. next state calc done")

def _write_state_file(generation: int, next_states: np.ndarray) -> None:
    """状態ファイル作成
    
    """
    start_time = time.time()
    
    file_path = TMP_REPORT_FOLDER + STATE_FILE_NAME2.replace("GENERATION", str(generation))
    np.save(file_path, next_states)
    
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
    