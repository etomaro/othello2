"""
世代ごとの状態数を算出する
"""
import csv
import time
from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME
from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.policy.negamax_player import NegaMaxPlayer
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate



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
    start_time = time.time()
    state_num = write_state_file(generation)
    write_anality_file(generation, state_num, start_time)

def write_state_file(generation: int) -> int:
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
        file_path, datas = create_initial_state_data()
    else:
        file_path, datas = create_state_data(generation)
    
    rows = [[data] for data in datas]
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    return len(datas)

def write_anality_file(generation: int, state_num: int, start_time: int):
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
    file_name = ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    file_path = REPORT_FOLDER + file_name
    
    calc_time = time.time() - start_time
    headers = ["状態数", "計算時間"]
    datas = [state_num, calc_time]
    
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(datas)

def create_initial_state_data() -> tuple[str, list[str]]:
    """
    世代0の状態数データを作成する
    
    return:
      file_path: ファイルパス
      datas: データ
    """
    ini_black_board = 0x0000000810000000
    ini_white_board = 0x0000001008000000
    ini_action_player_id = PlayerId.BLACK_PLAYER_ID.value
    generation = 0
    
    datas = [f"{ini_black_board}_{ini_white_board}_{ini_action_player_id}"]
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = REPORT_FOLDER + file_name
    
    return file_path, datas

def create_state_data(generation: int) -> tuple[str, list[str]]:
    """
    世代の状態数データを作成する
    
    1. 1つ前の世代のすべての状態数を取得する
    2. 状態数のアクション可能ハンドを取得する
    3. アクションを行い次の世代の状態を取得する
    4. 対称性を計算しカットできるか判定する
    
    return:
      file_path: ファイルパス
      datas: データ
    """
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = REPORT_FOLDER + file_name
    env = Env2()
    datas = []
    
    # 1. 1つ前の世代のすべての状態数を取得する
    states = get_state_file(generation -1)
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
            next_player_id = new_game_info.player_id
            
            # 状態作成
            next_state = f"{next_black_board}_{next_white_board}_{next_player_id}"
            datas.append(next_state)
            
            # TODO: 対称性
    
    return file_path, datas

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
    main(1)