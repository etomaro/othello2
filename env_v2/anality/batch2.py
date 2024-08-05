"""
2024/08/06 分析用のenvを作成
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

from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER
from env_v2.env_for_anality import get_initial_board, get_actionables, step, get_actionables_list
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.policy.negamax_player import NegaMaxPlayer
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate
from env_v2.symmetory.symmetory import get_symmetorys, get_symmetory_for_anality_batch

PLAYER_BLACK = 0
PLAYER_WHITE = 1
PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)

"""
状態数ファイル: {世代}_state.csv
分析ファイル: {世代}_anality.csv
"""
def batch(generation: int):
    """
    args
      generation: 世代
    """
    file_name_state = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path_state = TMP_REPORT_FOLDER + file_name_state
    file_name_analyty = ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    file_path_analyty = TMP_REPORT_FOLDER + file_name_analyty
    
    start_time = time.time()
    state_num, cut_sym = write_state_file(generation, file_path_state)
    write_anality_file(generation, state_num, start_time, file_path_analyty, cut_sym)

def write_state_file(generation: int, file_path: str) -> int:
    """
    状態数ファイルを作成する
    
    ファイル名: {世代}_state.csv
    項目: {black_board}_{white_board}_{次のアクションプレイヤーID}の列挙
    
    args:
      generation: 世代
    returns:
      state_num: 状態数
    """
    if generation == 0:
        datas, cut_sym = create_initial_state_data()
    else:
        datas, cut_sym = create_state_data_by_ray_states(generation)

    rows = [[data] for data in datas]
    write_start_time = time.time()
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        print("state file書き込み時間: ", time.time()-write_start_time)
    
    return len(datas), cut_sym

def write_anality_file(generation: int, state_num: int, start_time: int, file_path: str, cut_sym: int):
    """
    分析ファイルを作成する
    
    ファイル名: {世代}_anality.csv
    ヘッダー
      1. 状態数
      2. 計算時間
      
    args:
      generation: 世代
      state_num: 状態数
      start_time: 計測開始時間
    """
    calc_time = time.time() - start_time
    headers = ["状態数", "計算時間", "対称性カット数"]
    datas = [state_num, calc_time, cut_sym]
    
    write_start_time = time.time()
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(datas)
        print("anality file書き込み時間: ", time.time()-write_start_time)

def create_initial_state_data() -> list[str]:
    """
    世代0の状態数データを作成する
    
    return:
      datas: データ
    """
    ini_black_board = 0x0000000810000000
    ini_white_board = 0x0000001008000000
    ini_action_player_id = PLAYER_BLACK
    
    datas = [f"{ini_black_board}_{ini_white_board}_{ini_action_player_id}"]
    
    return datas, 0

def create_state_data_by_ray_states(generation: int) -> list[str]:
    """
    [バッチごと]世代の状態数データを作成する
    
    1. batchごとの分散処理ですべての次の状態を算出する開始
      1.1 対称性をすべて取得して次の状態を1意でもつ(対称性をつかって同じ状態の時に値として同じ状態で表せる)
    2. すべての次の状態を算出できるまで待つ
    3. 差分を消す
    
    return:
      datas: データ
    """
    context = ray.init()
    print(f"ray.init(): {context}")
    # 1. batchごとの分散処理ですべての次の状態を算出する開始
    read_start_time = time.time()
    states = get_state_file(generation -1)
    print("state file読込時間: ", time.time()-read_start_time)
    states_num = len(states)
    batch_num = 100000
    print(f"\n\n------------算出する世代:{generation}------------")
    print(f"計算するノード数: {states_num}")
    ray_ids = []
    proc_num = states_num//batch_num+1
    for i in range(1, proc_num):
        # 30GB
        ray_ids.append(batch_calc_state.remote(states[0: batch_num], i*batch_num, generation))
        del states[0: batch_num]
    ray_ids.append(batch_calc_state.remote(states, states_num, generation))
    del states
    print("非同期ですべての次の状態数を算出する処理を投下済み")
    
    # 2. すべての次の状態を算出できるまで待つ
    ray.get(ray_ids)
    
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
def batch_calc_state(states: list[str], index, generation) -> set[str]:
    """
    次の状態数を算出する
    """
    datas = set()
    count_for_cut = 0
    for state in states:
        black_board, white_board, player_id = state.split("_")
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
            next_state = f"{next_black_board}_{next_white_board}_{next_player_id}"
            datas.add(next_state)
            count_for_cut += 1
    
    cut_sym = count_for_cut - len(datas)
    
    # メモリにデータを登録しないようにstorageに登録する
    serialized = msgpack.packb((list(datas), cut_sym))
    file_path = TMP_REPORT_FOLDER + str(generation) + f"/{index}.bin"
    with open(file_path, "wb") as f:
        f.write(serialized)
        
    print(f"index: {index}. next state calc done")


def get_state_file(generation) -> list[str]:
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
        

