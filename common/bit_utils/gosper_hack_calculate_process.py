import csv

if __name__ == "__main__":

    # Gosper's hack計算過程をCSVに出力する(64C3)
    # 最初の3つと最後の3つを出力する。64C3の個数は41664
    count = 0
    datas = {}
    value = _get_patterns_by_gospers_hack(3)
    datas[value]