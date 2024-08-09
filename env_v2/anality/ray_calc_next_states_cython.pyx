
import csv
import time
import ray
import msgpack
import glob
import os

from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER,\
    BATCH_NUM
from env_v2.env_for_anality_cython import get_initial_board, get_actionables, step, get_actionables_list
from env_v2.symmetory.symmetory import get_symmetorys, get_symmetory_for_anality_batch

PLAYER_BLACK = 0
PLAYER_WHITE = 1
PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)


def ray_calc_next_states_cython(states: list[str], index, generation) -> set[str]:
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
    folder_path = TMP_REPORT_FOLDER + str(generation)
    file_path = folder_path + f"/{index}.bin"
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    with open(file_path, "wb") as f:
        f.write(serialized)
        
    print(f"index: {index}. next state calc done")