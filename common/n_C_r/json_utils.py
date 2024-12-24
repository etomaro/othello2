import json
from math import comb
import os


def _create_json_n_c_r(n: int):
    """
    nCrのr=0~nまでの数値をjsonファイルに出力

    作成ファイルパス: f"{n}.json"
    """
    datas = {}
    for r in range(0, n+1):
        pattern_num = comb(n, r)
        datas[r] = pattern_num 
    
    base_folder = os.path.dirname(__file__)
    file_path = base_folder + "/json_datas/" + f"{n}.json"
    with open(file_path, "w") as f:
        json.dump(datas, f, indent=2)
    

def read_json_n_c_r(n: int) -> dict:
    """
    jsonファイルを読み取り
    
    読み取りファイルパス: f"{n}.json"
    """
    base_folder = os.path.dirname(__file__)
    file_path = base_folder + "/json_datas/" + f"{n}.json"
    with open(file_path) as f:
        datas = json.load(f)
    
    return datas



if __name__ == "__main__":
    # Jsonファイル作成
    for i in range(1, 64+1):
        _create_json_n_c_r(i)