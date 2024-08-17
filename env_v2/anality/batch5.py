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
    
def _get_state_file(generation: int) -> np.ndarray:
    """
    returns:
        datas(numpy.ndarray) 状態の2重配列
    """
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = TMP_REPORT_FOLDER + file_name

    with open(file_path, "r") as f:
        rows = csv.reader(f)
        states = np.array(rows)  # 1行当たり1つの項目のみ

    return states

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
    next_states = None
    for file in files:
        with open(file, "rb") as f:
            deserialized = msgpack.load(f, raw=False)
            cut_num += deserialized[1]
            if next_states is not None:
                next_states = np.concatenate([next_states, deserialized[0]])
            else:
                next_states = np.array(deserialized[0])
    
    # 重複を削除していない次の状態数
    next_state_num = next_states.shape[0]
    # 次の状態の重複を削除する
    next_states = np.unique(next_states, axis=0)
    cut_num += next_state_num - next_states.shape[0]
    return next_states, cut_num

@ray.remote(max_retries=-1)
def _ray_calc_next_states(states: np.ndarray, index, generation):
    """
    次の状態数を算出する
    
    1. ゲームが終了している場合除外する
    2. アクション可能ハンドを取得する
    3. アクションを行う
    4. 対称性を利用して除外する
    5. 次の状態のリストに追加する
    """
    # 1. ゲームが終了している場合除外する
    states = states[states[:, 2] != PLAYER_UNKNOW]
    # 2. アクション可能ハンドを取得する
    actions = get_actions(list(states))
    # 3. アクションを行う
    next_states = step_parallel(np.array(actions))
    
    
    
    datas = set()
    count_for_cut = 0
    for state in states:
        black_board, white_board, player_id = state
        # ゲーム終了してる場合
        if player_id == PLAYER_UNKNOW:
            continue
        
        black_board, white_board, player_id =\
            int(black_board), int(white_board), int(player_id)
        
        # 2. 状態数のアクション可能ハンドを取得する
        actionables = get_actionables(black_board, white_board, player_id)
        actionable_list = get_actionables_list(actionables)
        
        # 3. アクションを行い次の世代の状態を取得する
        for action in actionable_list:
            # アクション
            next_black_board, next_white_board, next_player_id = step(black_board, white_board, player_id, action)
            
            # 対称性の中から1意となるように状態を変換
            next_black_board, next_white_board = get_symmetory_for_anality_batch(next_black_board, next_white_board)
            
            # 状態作成
            next_state = (next_black_board, next_white_board, next_player_id)
            datas.add(next_state)
            count_for_cut += 1
    
    cut_sym = count_for_cut - len(datas)
    
    # メモリにデータを登録しないようにstorageに登録する
    serialized = msgpack.packb((list(datas), cut_sym))
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
    