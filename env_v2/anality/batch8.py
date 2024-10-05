"""
2024/08/26 HDFを使用

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
import h5py
from numpy import int64
import dask.array as da
from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER,\
    BATCH_NUM, STATE_FILE_NAME2, STATE_FILE_NAME3
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
        calc_time = 0
        calc_sum_time = 0
        # 3. 状態ファイル作成
        next_state_num = _write_state_file_init()
    else:
        # 1世代前の状態ファイルを読み取る
        states = _get_state_file(generation-1)
        # 2. 状態の算出
        calc_start_time = time.time()
        _calc_next_states(generation, states)
        calc_time = time.time() - calc_start_time
        # 3. 状態ファイル作成
        calc_sum_start_time = time.time()
        next_state_num = _write_state_file(generation)
        calc_sum_time = time.time() - calc_sum_start_time
    
    # 4. 分析ファイル作成
    total_time = time.time() - start_time
    _write_anality_file(generation, next_state_num, total_time, calc_time, calc_sum_time)
    
def _get_state_file(generation: int) -> da.Array:
    """
    returns:
        datas(numpy.ndarray) 状態の2重配列
    """
    file_name = STATE_FILE_NAME3.replace("GENERATION", str(generation))
    file_path = TMP_REPORT_FOLDER + file_name

    # hd5を読み取り
    with h5py.File(file_path, "r") as f:
        dataset = f["state"]
        states = da.from_array(dataset[...])
    
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

def _calc_next_states(generation: int, states: da.Array) -> tuple[np.ndarray, np.ndarray]:
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
    
    context = ray.init()
    print("dashboard: ", context)
    calc_state_num = states.compute_chunk_sizes().shape[0]  # 計算する1つ前の世代のノード数
    print("calc_state_num: ", calc_state_num)
    proc_num = calc_state_num // BATCH_NUM + 1  # 計算するプロセス数
    print("proc_num: ", proc_num)
    print(f"算出するノード数: {calc_state_num}")
    
    # Queueにタスクをすべて投入する
    ray_ids = []
    index = 0
    for _ in range(1, proc_num):
        # putを使うことでメモリ節約になるらしい
        # https://yuiga.dev/blog/posts/rayremote%E3%81%8C%E3%83%A1%E3%83%A2%E3%83%AA%E3%82%92%E5%A4%A7%E9%87%8F%E3%81%AB%E9%A3%9F%E3%81%86%E6%99%82%E3%81%AFray.put%E3%82%92%E4%BD%BF%E3%81%8A%E3%81%86/
        ray_id = ray.put(states[index: index+BATCH_NUM][:].compute())
        ray_ids.append(_ray_calc_next_states.remote(ray_id, index+BATCH_NUM, generation))
        index += BATCH_NUM
        # TODO: np.deleteは新しいオブジェクトを生成するためメモリ効率悪い
        # states =  np.delete(states, slice(0,BATCH_NUM), axis=0)
    try:
        ray_id = ray.put(states[index:][:].compute())
        ray_ids.append(_ray_calc_next_states.remote(ray_id, calc_state_num, generation))
    except IndexError:
        pass
    del states
    print("非同期ですべての次の状態数を算出する処理を投下済み")
    
     # 2. すべての次の状態を算出できるまで待つ
    ray.get(ray_ids)
    ray.shutdown()
    del ray_ids
    
    print("全ての状態の算出終了!!!")

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
    print("states type: ", type(states))
    print("states num: ", states.shape[0])
    # 2. アクション可能ハンドを取得する
    actions = get_actions(states)
    # メモリ削減用
    del states
    # print("actions: ", actions)
    # 3. アクションを行う(対称性も使用)
    dummy = np.zeros(3, dtype=np.uint64)
    # print("dummy: ", dummy)
    next_states = step_parallel(actions, dummy)
    # 要素が1つの場合1次元配列になるので注意
    if next_states.ndim == 1:
        next_states = next_states.reshape(1,3)
    
    # メモリ削減用
    del actions
    
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

def _write_state_file(generation: int) ->  int:
    """状態ファイル作成
    
    returns:
      next_state_num: 算出した世代の状態の個数
    """
    # stateファイルを作成する
    state_file_path = TMP_REPORT_FOLDER + STATE_FILE_NAME3.replace("GENERATION", str(generation))
    with h5py.File(state_file_path, "w") as f:
        # データセットを作成する
        f.create_dataset("state", (0, 3), maxshape=(None, 3), chunks=(100000, 3), dtype=np.uint64)
    
    # TODO: batchごとではなくもう少し大きいサイズでやった方が効率的
    # ファイルを一括取得する
    files = glob.glob(f"env_v2/anality/report/tmp/{generation}/*")
    next_state_num = 0
    cut_num = 0  # 対称性でカットした回数
    for i, file in enumerate(files):
        # ファイルパスから拡張子を除いたファイル名を取得
        file_name = os.path.splitext(os.path.basename(file))[0]
        _, tmp_cut_num = file_name.split("_")
        cut_num+=int(tmp_cut_num)
        # ファイル読み込み
        states = np.load(file)
        next_state_num += states.shape[0]
        # tupleに変形
        states = tuple(map(tuple, states))
        
        # 他のファイルから重複する値を削除する
        for other_file in files[i+1:]:
            other_state = np.load(other_file)
            """重複している値を除いてファイルを上書き保存する
            2重リストまたは2次元numpy配列はsetを使えない。
            また、並行で差分を取得する関数がないためtupleに変形してsetで差分を取得する
            """
            other_state = tuple(map(tuple, other_state))
            other_state_not_duplicate = np.array(list(set(other_state) - set(states)), dtype=np.uint64)
            np.save(other_file, other_state_not_duplicate)
        
        # uniqueな値を登録する
        with h5py.File(state_file_path, "a") as f:
            dset = f["state"]
            # numpyに戻す
            states = np.array(states, dtype=np.uint64)
            # サイズを変更する
            current_size = dset.shape[0]
            dset.resize(dset.shape[0] + states.shape[0], axis=0)
            # 追加
            dset[current_size:] = states
    
    return next_state_num
    
def _write_state_file_init() ->  int:
    """状態ファイル作成
    
    returns:
      next_state_num: 算出した世代の状態の個数
    """
    generation = 0
    
    # stateファイルを作成する
    state_file_path = TMP_REPORT_FOLDER + STATE_FILE_NAME3.replace("GENERATION", str(generation))
    with h5py.File(state_file_path, "w") as f:
        # データセットを作成する
        dset = f.create_dataset("state", (1, 3), chunks=(1, 3), dtype=np.uint64)
        
        ini_black_board = 0x0000000810000000
        ini_white_board = 0x0000001008000000
        ini_player_id = PLAYER_BLACK
    
        ini_states = np.array([[ini_black_board, ini_white_board, ini_player_id]],dtype=np.uint64)
        dset[...] = ini_states
    
    return 1

def _write_anality_file(generation: int, state_num: int, total_time: int, calc_time: int, calc_sum_time: int) -> None:
    """分析ファイル作成
    
    """
    HEADERS = ["状態数", "Total計算時間", "次の状態算出までの時間", "次の状態を一括するまでの時間"]
    
    file_path = TMP_REPORT_FOLDER + ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerow([state_num, total_time, calc_time, calc_sum_time])
    