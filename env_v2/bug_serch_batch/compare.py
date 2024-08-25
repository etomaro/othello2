"""
action取得、次の状態算出、対称性取得を比較する

※ すべてListとして比較する
"""
from env_v2.anality.settings import *
import csv
from env_v2.env_for_anality import step, get_actionables, get_actionables_list
from env_v2.symmetory.symmetory import get_symmetory_for_anality_batch
from env_v2.env_by_numpy import get_actions, step_parallel
import numpy as np
from numpy import int64

# ----------1つ前のstateファイル読み込み----------
def read_state_after(generation) -> list:
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "../anality/report/tmp/" + file_name

    states = np.loadtxt(file_path, delimiter=',', dtype=np.uint64)
    states = states.tolist()
    return states

def read_state_before(generation) -> list:
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "../anality/report/20240812/" + file_name

    states = np.loadtxt(file_path, delimiter=',', dtype=np.uint64)
    states = states.tolist()
    return states

# ----------アクション結果を取得----------
def get_actions_before(states) -> list:
    actions = []
    for state in states:
        bb, wb, pi = int(state[0]), int(state[1]), int(state[2])
        actionables = get_actionables(bb,wb,pi)
        actionables_list = get_actionables_list(actionables)
        for action in actionables_list:
            actions.append([bb, wb, pi, action])

    return actions

def get_actions_after(states):
    actions = get_actions(states)
    return actions

# ----------次の状態を取得(対称性なし)----------
def get_next_states_before(states) -> list:
    next_states = []
    for state in states:
        bb, wb, pi = int(state[0]), int(state[1]), int(state[2])
        actionables = get_actionables(bb,wb,pi)
        actionables_list = get_actionables_list(actionables)
        for action in actionables_list:
            next_bb, next_wb, next_pi = step(bb, wb, pi, action)
            next_states.append([next_bb, next_wb, next_pi])

    return next_states

def get_next_states_after(states: list) -> list:
    actions = get_actions(states)
    dummy = np.zeros(3, dtype=np.uint64)
    actions = np.array(actions, dtype=np.uint64)
    # !!!!この関数を使用する場合ste_parallelの対称性をコメントアウトする必要あり!!!!
    next_states = step_parallel(actions, dummy)
    next_states = next_states.tolist()
    return next_states

# ----------次の状態を取得(対称性あり)----------
def get_next_states_sym_before(states) -> list:
    actions = []
    for state in states:
        bb, wb, pi = int(state[0]), int(state[1]), int(state[2])
        actionables = get_actionables(bb,wb,pi)
        actionables_list = get_actionables_list(actionables)
        for action in actionables_list:
            next_bb, next_wb, next_pi = step(bb, wb, pi, action)
            next_bb, next_wb = get_symmetory_for_anality_batch(next_bb, next_wb)
            actions.append([next_bb, next_wb, next_pi])

    return actions

def get_next_states_sym_after(states) -> list:
    actions = get_actions(states)
    dummy = np.zeros(3, dtype=np.uint64)
    actions = np.array(actions, dtype=np.uint64)
    next_states = step_parallel(actions, dummy)
    next_states = next_states.tolist()
    return next_states

# --------------比較--------------


# 0. 読み取ったstateの違い
# 1. ACTION
# 2. NEXT_STATES
# 3. NEXT_STATES(対称性)
SETTINGS = 3
GENERATION = 3
states_before = read_state_before(GENERATION)
states_after = read_state_after(GENERATION)

# 0. 読み取ったstateの違い
if SETTINGS == 0:
    print("------------比較(個数)----------------")
    print("変更前の個数: ", len(states_before))
    print("変更後の個数: ", len(states_after))
    print("------------順番比較----------------")
    for i in range(len(states_before)):
        if states_before[i] != states_after[i]:
            print("index: ", i)
            print("変更前のaction: ", states_before[i])
            print("変更後のaction: ", states_after[i])
            break

# 1. ACTION
elif SETTINGS == 1:
    actions_before = get_actions_before(states_before)
    actions_after = get_actions_after(states_after)
    # 数が多いためコメントアウト
    # print("-------------変更前--------------")
    # print(actions_before)
    # print("------------変更後--------------")
    # print(actions_after)
    print("------------比較(個数)----------------")
    print("変更前の個数: ", len(actions_before))
    print("変更後の個数: ", len(actions_after))
    print("------------比較(差分)----------------")
    diff_actions_not_in_after = []
    for action in actions_before:
        if action not in actions_after:
            diff_actions_not_in_after.append(action)

    diff_actions_not_in_before = []
    for action in actions_after:
        if action not in actions_before:
            diff_actions_not_in_before.append(action)

    print("変更前に存在し変更後に存在しない個数: ", len(diff_actions_not_in_after))
    print("変更後に存在し変更前に存在しない個数: ", len(diff_actions_not_in_before))
    print("変更前に存在し変更後に存在しないもの")
    print(diff_actions_not_in_after)
    print("変更後に存在し変更前に存在しないもの")
    print(diff_actions_not_in_before)
    
    print("------------順番比較(順番が異なる場合最初の一つ目を出力)----------------")
    for i, action in enumerate(actions_before):
        if actions_before[i] != actions_after[i]:
            print("index: ", i)
            print("変更前のアクション: ", actions_before[i])
            print("変更後のアクション: ", actions_after[i])
            break
    
    print("------------状態とアクションのmap------------")
    # {BLACK_BOARD}_{WHITE_BOARD}: [action]の辞書を作成して順番をチェックする
    dict_before = {}
    dict_after = {}
    for state_before in states_before:
        tmp_actions_before = get_actions_before([state_before])
        for tmp_action_before in tmp_actions_before:
            key = f"{tmp_action_before[0]}_{tmp_action_before[1]}"
            value = f"{tmp_action_before[2]}"
            dict_before.setdefault(key, []).append(value)
            
    for state_after in states_after:
        tmp_actions_after = get_actions_after([state_after])
        for tmp_action_after in tmp_actions_after:
            key = f"{tmp_action_after[0]}_{tmp_action_after[1]}"
            value = f"{tmp_action_after[2]}"
            dict_after.setdefault(key, []).append(value)
    
    print("keyの順番が異なる")
    for i, state_action in enumerate(dict_before.keys()):
        if list(dict_before.keys())[i] != list(dict_after.keys())[i]:
            print("index: ", i)
            print("変更前のkey: ", list(dict_before.keys())[i])
            print("変更後のkey: ", list(dict_after.keys())[i])
            print("変更前のstate: ", states_before[i])
            print("変更後のstate: ", states_after[i])
            break
    
    print("actionが異なる")
    for state_action, _ in dict_before.items():
        if dict_before[state_action] != dict_after[state_action]:
            print("state: ", state_action)
            print("変更前のaction: ", dict_before[state_action])
            print("変更後のaction: ", dict_after[state_action])
    
# 2. NEXT_STATES
elif SETTINGS == 2:
    next_states_before = get_next_states_before(states_before)
    next_states_after = get_next_states_after(states_after)

    print("------------比較(個数)----------------")
    print("変更前の個数: ", len(next_states_before))
    print("変更後の個数: ", len(next_states_after))
    print("------------比較(差分)----------------")
    diff_next_states_not_in_after = []
    for next_state in next_states_before:
        if next_state not in next_states_after:
            diff_next_states_not_in_after.append(next_state)

    diff_next_states_not_in_before = []
    for next_state in next_states_after:
        if next_state not in next_states_before:
            diff_next_states_not_in_before.append(next_state)

    print("変更前に存在し変更後に存在しない個数: ", len(diff_next_states_not_in_after))
    print("変更後に存在し変更前に存在しない個数: ", len(diff_next_states_not_in_before))
    print("変更前に存在し変更後に存在しないもの")
    print(diff_next_states_not_in_after)
    print("変更後に存在し変更前に存在しないもの")
    print(diff_next_states_not_in_before)
    
    print("------------順番比較(順番が異なる場合最初の一つ目を出力)----------------")
    for i, next_state_before in enumerate(next_states_before):
        if next_states_before[i] != next_states_after[i]:
            print("index: ", i)
            print("変更前の次のstate: ", next_states_before[i])
            print("変更後の次のstate: ", next_states_after[i])
            break

# # 3. NEXT_STATES(対称性)
elif SETTINGS == 3:
    next_states_before = get_next_states_sym_before(states_before)
    next_states_after = get_next_states_sym_after(states_after)

    print("------------比較(個数)----------------")
    print("変更前の個数: ", len(next_states_before))
    print("変更後の個数: ", len(next_states_after))
    print("------------比較(差分)----------------")
    diff_next_states_not_in_after = []
    for next_state in next_states_before:
        if next_state not in next_states_after:
            diff_next_states_not_in_after.append(next_state)

    diff_next_states_not_in_before = []
    for next_state in next_states_after:
        if next_state not in next_states_before:
            diff_next_states_not_in_before.append(next_state)

    print("変更前に存在し変更後に存在しない個数: ", len(diff_next_states_not_in_after))
    print("変更後に存在し変更前に存在しない個数: ", len(diff_next_states_not_in_before))
    print("変更前に存在し変更後に存在しないもの")
    print(diff_next_states_not_in_after)
    print("変更後に存在し変更前に存在しないもの")
    print(diff_next_states_not_in_before)
    
    print("------------順番比較(順番が異なる場合最初の一つ目を出力)----------------")
    for i, next_state_before in enumerate(next_states_before):
        if next_states_before[i] != next_states_after[i]:
            print("index: ", i)
            print("変更前の次のstate: ", next_states_before[i])
            print("変更後の次のstate: ", next_states_after[i])
            break