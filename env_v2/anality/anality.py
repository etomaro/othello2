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
    
    write_csv(file_path, datas)
    
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
    HEADERS = ["状態数", "計算時間"]
    datas = [HEADERS, [state_num, calc_time]]
    
    write_csv(file_path, datas)

def create_initial_state_data() -> tuple[str, list[list[str]]]:
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
    
    datas = [[f"{ini_black_board}_{ini_white_board}_{ini_action_player_id}"]]
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = REPORT_FOLDER + file_name
    
    return file_path, datas
    
def write_csv(file_path: str, datas: list[list[str]]):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(datas)
        
        
if __name__ == "__main__": 
  main(0)