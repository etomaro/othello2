import glob
import msgpack
import csv
from env_v2.anality.settings import REPORT_FOLDER, STATE_FILE_NAME, ANALITY_FILE_NAME, TMP_REPORT_FOLDER
import time


if __name__ == "__main__":
    generation = 12
    file_name_state = STATE_FILE_NAME.replace("GENERATION", str(generation))
    file_path_state = TMP_REPORT_FOLDER + file_name_state
    file_name_analyty = ANALITY_FILE_NAME.replace("GENERATION", str(generation))
    file_path_analyty = TMP_REPORT_FOLDER + file_name_analyty

    # ファイルを一括取得する
    files = glob.glob(f"env_v2/anality/report/tmp/{generation}/*")
    state_num = 0
    cut_num = 0  # 対称性でカットした回数
    next_states_set = set()
    print(f"file数: {len(files)}")
    import sys
    for i, file in enumerate(files):
        with open(file, "rb") as f:
            deserialized = msgpack.load(f, raw=False)
            state_num += len(deserialized[0])
            cut_num += deserialized[1]
            next_states_set |= set(deserialized[0])
        print(f"{i}. done size: {next_states_set.__sizeof__()}")
        print(f"{i}. done size: {sys.getsizeof(next_states_set)}")
        if i == 50:
            time.sleep(20)
        
    
    cut_num += state_num - len(next_states_set)
    
    print("全tmpファイル読み込み成功")
    
    
    rows = [[data] for data in next_states_set]
    with open(file_path_state, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    headers = ["状態数", "計算時間", "対称性カット数"]
    datas = [state_num, None, cut_num]
    
    with open(file_path_analyty, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(datas)