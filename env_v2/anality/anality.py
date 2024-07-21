"""
世代ごとの状態数を算出する
"""
import csv
import time
import ray
from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER
from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.policy.negamax_player import NegaMaxPlayer
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate
from env_v2.symmetory.symmetory import get_symmetorys


PLAYER_ID_NONE = 999

"""
状態数ファイル: {世代}_state.csv
分析ファイル: {世代}_anality.csv
"""
def main(generation: int):
    """
    args
      generation: 世代
    """
    file_name_state = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path_state = TMP_REPORT_FOLDER + file_name_state
    file_name_analyty = ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    file_path_analyty = TMP_REPORT_FOLDER + file_name_analyty
    
    start_time = time.time()
    state_num, sym_count = write_state_file(generation, file_path_state)
    write_anality_file(generation, state_num, start_time, file_path_analyty, sym_count)

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
        datas, sym_count = create_initial_state_data()
    else:
        # datas, sym_count = create_state_data(generation)
        
        datas, sym_count = create_state_data_by_ray_states(generation)
    
    rows = [[data] for data in datas]
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    return len(datas), sym_count

def write_anality_file(generation: int, state_num: int, start_time: int, file_path: str, sym_count: int):
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
    datas = [state_num, calc_time, sym_count]
    
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(datas)

def create_initial_state_data() -> list[str]:
    """
    世代0の状態数データを作成する
    
    return:
      datas: データ
    """
    ini_black_board = 0x0000000810000000
    ini_white_board = 0x0000001008000000
    ini_action_player_id = PlayerId.BLACK_PLAYER_ID.value
    
    datas = [f"{ini_black_board}_{ini_white_board}_{ini_action_player_id}"]
    
    return datas, 0

def create_state_data(generation: int) -> list[str]:
    """
    世代の状態数データを作成する
    
    1. 1つ前の世代のすべての状態数を取得する
    2. 状態数のアクション可能ハンドを取得する
    3. アクションを行い次の世代の状態を取得する
    4. 対称性を計算しカットできるか判定する
    
    return:
      datas: データ
    """
    env = Env2()
    datas = []
    
    # 1. 1つ前の世代のすべての状態数を取得する
    states = get_state_file(generation -1)
    print(f"\n\n------------算出する世代:{generation}------------")
    print(f"計算するノード数: {len(states)}")
    count_sym = 0  # 対称性でカットした回数
    for i, state in enumerate(states):
        black_board, white_board, player_id = state.split("_")
        # ゲーム終了してる場合
        if player_id == PLAYER_ID_NONE:
            continue
        
        black_board, white_board, player_id =\
            int(black_board), int(white_board), int(player_id)
        
        # 2. 状態数のアクション可能ハンドを取得する
        actionables = env.get_actionables(black_board, white_board, player_id)
        actionable_list = env.get_actionables_list(actionables)
        
        # 3. アクションを行い次の世代の状態を取得する
        for action in actionable_list:
            game_info = GameInfo(
                black_board=black_board,
                white_board=white_board,
                player_id=player_id,
                actionables=actionables,
                game_state=GameState.IN_GAME,
                generation=generation-1  # 0スタート
            )
            # アクション
            new_game_info = env.step(game_info, action)
            next_black_board = new_game_info.black_board
            next_white_board = new_game_info.white_board
            next_player_id = new_game_info.player_id if new_game_info.player_id is not None else 999
            
            # 状態作成
            next_state = f"{next_black_board}_{next_white_board}_{next_player_id}"
            
            # 対称性取得
            next_symmetorys = get_symmetorys(next_black_board, next_white_board)
            next_states_symmetory = change_to_states(next_symmetorys, next_player_id)  # 状態の持ち方を変更する
            # 既に対称性が登録されている場合登録しない
            if not set(datas) & set(next_states_symmetory):
                datas.append(next_state)
            else:
                count_sym += 1
        
        # 1000ごとに出力
        if i%1000 == 0:
            print(f"{i}. calc node done")
    
    return datas, count_sym

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
    env = Env2()
    # 1. batchごとの分散処理ですべての次の状態を算出する開始
    states = get_state_file(generation -1)
    states_num = len(states)
    batch_num = 1000
    print(f"\n\n------------算出する世代:{generation}------------")
    print(f"計算するノード数: {states_num}")
    count_sym = 0  # 対称性でカットした回数
    ray_ids = []
    proc_num = states_num//batch_num + 1
    for i in range(1, proc_num+1):
        ray_ids.append(batch_calc_state.remote(states[0: batch_num], i*batch_num, generation))
        del states[0: batch_num]
    ray_ids.append(batch_calc_state.remote(states, states_num, generation))
    del states
    print("非同期ですべての次の状態数を算出する処理を投下済み")
    
    # 2. すべての次の状態を算出できるまで待つ
    next_states_two_dim = ray.get(ray_ids)
    next_states_set = []  # 2次元を1次元にする
    for array in next_states_two_dim:
        next_states_set += array
    next_states_set = set(next_states_set)
    
    # 3. batchごとの分散処理ですべての状態に対してそれぞれ対称性がないもののみ取得する
        
        
    
    
    return list(next_states_set), count_sym

def create_state_data_by_ray_state(generation: int) -> list[str]:
    """
    [1stateごと]世代の状態数データを作成する
    
    1. batchごとの分散処理ですべての次の状態を算出する開始
    2. すべての次の状態を算出できるまで待つ
    3. batchごとの分散処理ですべての状態に対してそれぞれ対称性がないもののみ取得する
    4. すべての対称性がないものを取得できるまで待つ
    5. すべての対称性がないものと次の状態の差分を取得する(=対称性がすくなくても1つ以上存在するもの)
    6. 差分を1つずつ処理し対称性で同じものを1つだけ取り出す
    7. 2と6をマージして保存
    
    return:
      datas: データ
    """
    env = Env2()
    datas = []    
    # 1. batchごとの分散処理ですべての次の状態を算出する開始
    states = get_state_file(generation -1)
    states_num = len(states)
    batch_num = 5000
    print(f"\n\n------------算出する世代:{generation}------------")
    print(f"計算するノード数: {states_num}")
    count_sym = 0  # 対称性でカットした回数
    ray_ids = []
    proc_num = states_num//batch_num + 1
    for i in range(1, proc_num+1):
        ray_ids.append(batch_calc_state.remote(states[0: batch_num], i*batch_num, generation))
        del states[0: batch_num]
    ray_ids.append(batch_calc_state.remote(states, states_num, generation))
    del states
    print("非同期ですべての次の状態数を算出する処理を投下済み")
    
    # 2. すべての次の状態を算出できるまで待つ
    next_states = ray.get(ray_ids)
    
    # 3. batchごとの分散処理ですべての状態に対してそれぞれ対称性がないもののみ取得する
        
        
    
    
    return datas, count_sym

@ray.remote
def batch_calc_state(states: list[str], index, generation) -> set[str]:
    """
    次の状態数を算出する
    """
    env = Env2()
    datas = set()
    for state in states:
        black_board, white_board, player_id = state.split("_")
        # ゲーム終了してる場合
        if player_id == PLAYER_ID_NONE:
            continue
        
        black_board, white_board, player_id =\
            int(black_board), int(white_board), int(player_id)
        
        # 2. 状態数のアクション可能ハンドを取得する
        actionables = env.get_actionables(black_board, white_board, player_id)
        actionable_list = env.get_actionables_list(actionables)
        
        # 3. アクションを行い次の世代の状態を取得する
        for action in actionable_list:
            game_info = GameInfo(
                black_board=black_board,
                white_board=white_board,
                player_id=player_id,
                actionables=actionables,
                game_state=GameState.IN_GAME,
                generation=generation-1  # 0スタート
            )
            # アクション
            new_game_info = env.step(game_info, action)
            next_black_board = new_game_info.black_board
            next_white_board = new_game_info.white_board
            next_player_id = new_game_info.player_id if new_game_info.player_id is not None else 999
            
            # 状態作成
            next_state = f"{next_black_board}_{next_white_board}_{next_player_id}"
            datas.add(next_state)
        
    print(f"index: {index}. next state calc done")
    
    return datas

def change_to_states(symmetorys: list[tuple], player_id: int) -> list[str]:
    """
    状態を{black_board}_{white_board}_{player_id}に変換する
    """
    states = []
    for black_board, white_board in symmetorys:
         state = f"{black_board}_{white_board}_{player_id}"
         states.append(state)
    
    return states

def get_state_file(generation) -> list[str]:
    """
    returns:
      datas: 状態のリスト
    """
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = REPORT_FOLDER + file_name
    
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        datas = [row[0] for row in reader]  # 1行当たり1つの項目のみ
    
    return datas
        
        
if __name__ == "__main__":
    # for i in range(10):
    #     main(i)
    
    main(9)