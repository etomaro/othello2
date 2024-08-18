from env_v2.anality.settings import *
import csv
from env_v2.env_for_anality import step, get_actionables, get_actionables_list
from env_v2.symmetory.symmetory import get_symmetory_for_anality_batch
from env_v2.env_by_numpy import get_actions, step_parallel
import numpy as np
from numpy import int64

def read_state_file_numpy(generation):
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "anality/report/tmp/" + file_name

    with open(file_path, "r") as f:
        rows = csv.reader(f)
        states = list(rows)
    return states

def read_state_file(generation):
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "anality/report/20240812/" + file_name

    with open(file_path, "r") as f:
        rows = csv.reader(f)
        states = list(rows)
    return states

def get_actions_before(states):
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

def get_actions_after(states):
    actions = get_actions(states.tolist())
    dummy = np.zeros(3, dtype=int64)
    actions = np.array(actions)
    next_states = step_parallel(actions, dummy)
    next_states = next_states.tolist()
    # 変更前の対称性を使用
    result = []
    for state in next_states:
        next_bb, next_wb = get_symmetory_for_anality_batch(state[0],state[1])
        result.append([next_bb,next_wb,state[2]])
    return result

print("-------------変更前--------------")
states1 = read_state_file(2)
next_states1 = get_actions_before(states1)
print(next_states1)

print("------------変更後--------------")
states2 = read_state_file_numpy(2)
states2 = np.array(states2, dtype=int64)
next_states2 = get_actions_after(states2)
print(next_states2)

print("------------比較----------------")
print("変更前の個数: ", len(next_states1))
print("変更後の個数: ", len(next_states2))
diff_states1 = []
for state in next_states1:
    if state not in next_states2:
        diff_states1.append(state)

diff_states2 = []
for state in next_states2:
    if state not in next_states1:
        diff_states2.append(state)

print("変更前に存在し変更後に存在しない個数: ", len(diff_states1))
print("変更後に存在し変更前に存在しない個数: ", len(diff_states2))
print("変更前に存在し変更後に存在しないもの")
print(diff_states1)
print("変更後に存在し変更前に存在しないもの")
print(diff_states2)


