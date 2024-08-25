from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER,\
    BATCH_NUM
import csv
from env_v2.symmetory.symmetory import get_symmetorys, get_symmetory_for_anality_batch


# 変更前のstateを取得する
def get_old_states(generation):
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "../anality/report/20240812/" + file_name

    with open(file_path, "r") as f:
        rows = csv.reader(f)
        states = list(rows)  # 1行当たり1つの項目のみ

    return states

def get_new_states(generation):
    file_name = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path = "../anality/report/tmp/" + file_name

    with open(file_path, "r") as f:
        rows = csv.reader(f)
        states = list(rows)  # 1行当たり1つの項目のみ

    return states

generation = 7
old_states = get_old_states(generation)
new_states = get_new_states(generation)

# 新しい状態を古い対称性関数を使用
new_states_sym = []
for state in new_states:
    bb_sym, wb_sym = get_symmetory_for_anality_batch(int(state[0]), int(state[1]))
    new_states_sym.append([str(bb_sym), str(wb_sym), state[2]])

# 比較
diff_not_in_new = []  #　新しい状態に存在しない古い状態
for old_state in old_states:
    if old_state not in new_states_sym:
        diff_not_in_new.append(old_state)

diff_not_in_old = []  # 古い状態に存在しない新しい状態
for new_state in new_states_sym:
    if new_state not in old_states:
        diff_not_in_old.append(new_state)

print("新しい状態に存在しない古い状態の数: ", len(diff_not_in_new))
print("古い状態に存在しない新しい状態の数: ", len(diff_not_in_old))
print("---------------------------------------------------------")
print("新しい状態に存在しない古い状態")
for state in diff_not_in_new:
    print(state)
print("古い状態に存在しない新しい状態")
for state in diff_not_in_old:
    print(state)
