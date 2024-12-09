"""
状態のnumpy, arrayのメモリ使用量と実際の情報量を比較する
"""
import numpy as np
import csv
import matplotlib.pyplot as plt
import japanize_matplotlib

def get_element_one():
    """
    変数のめもり使用量をprint出力する
    """
    black_state_zero = 0x0
    black_state_full = 0xffffffffffffffff
    black_state_array_zero = [0x0]
    black_state_array_full = [0xffffffffffffffff]
    black_state_numpy_zero = np.array([0x0])
    black_state_numpy_full = np.array([0xffffffffffffffff])


    """
    [black_state_zero]__sizeof__(): 24 byte -> 実情報量の3倍
    [black_state_full]__sizeof__(): 36 byte -> 実情報量の4.5倍
    [black_state_array_zero]__sizeof__(): 48 byte -> 実情報量の6倍
    [black_state_array_full]__sizeof__(): 48 byte -> 実情報量の6倍
    [black_state_numpy_zero]__sizeof__(): 120 byte -> 実情報量の15倍
    [black_state_numpy_full]__sizeof__(): 120 byte -> 実情報量の15倍
    [black_state_numpy_zero]nbytes: 8byte -> 実情報量
    [black_state_numpy_full]nbytes: 8byte -> 実情報量
    """
    print(f"[black_state_zero]__sizeof__(): {black_state_zero.__sizeof__()} byte")
    print(f"[black_state_full]__sizeof__(): {black_state_full.__sizeof__()} byte")
    print(f"[black_state_array_zero]__sizeof__(): {black_state_array_zero.__sizeof__()} byte")
    print(f"[black_state_array_full]__sizeof__(): {black_state_array_full.__sizeof__()} byte")
    print(f"[black_state_numpy_zero]__sizeof__(): {black_state_numpy_zero.__sizeof__()} byte")
    print(f"[black_state_numpy_full]__sizeof__(): {black_state_numpy_full.__sizeof__()} byte")
    print(f"[black_state_numpy_zero]nbytes: {black_state_numpy_zero.nbytes} byte")  # <ndarray>.nbytes:  要素の情報量だけのサイズ
    print(f"[black_state_numpy_full]nbytes: {black_state_numpy_full.nbytes} byte")
    

def get_array_memoy_relation(step: int,  ele_num_max: int):
    """
    状態の実際の情報量と配列、メモリの要素ごとサイズを比較する
    
    ファイルに出力するデータ
      要素数 実際の情報量 実際の情報量とarrayの差分 実際の情報量とnp.ndarrayの差分 array    np.ndarray
        1      8bytes            16bytes                 0                    24bytes   16bytes
        ...
    
    args:
      step: 要素数の幅数
      ele_num_max: 調べる最大の要素数
    """

    def change_to_unit(value):
        """
        単位を変更する

        B, KB, MB, GB, TB
        """
        b_unit = 1000
        kb_unit = b_unit * 1000
        mb_unit = kb_unit * 1000
        gb_unit = mb_unit * 1000
        tb_unit = gb_unit * 1000

        pass

    ele = 0xffffffffffffffff  # 全ての要素は固定とする
    real_size_by_ele = 64  # 実際の1要素(状態)のサイズは64bit
    num_by_100 = (ele_num_max//step) //100  # 処理経過を1%ごとに出力する

    real_size = 0
    array = []
    
    headers = ["要素数", "実際の情報量", "実際の情報量とarrayの差分", "実際の情報量とndrrayの差分", "配列のメモリ使用量", "ndarrayのメモリ使用量"]
    rows = []
    
    for idx, ele_num in enumerate(range(step, ele_num_max+1, step)):
        array.extend([ele]*step)
        real_size += real_size_by_ele*step  # 実際の情報量
        # __sizeof__()はbyte表記のため8倍する
        array_np_size = np.array(array).__sizeof__()*8  # ndarrayの情報量
        array_size = array.__sizeof__()*8  # arrayの情報量
        array_diff = array_size - real_size  # 実際の情報量とarrayの差分
        array_np_diff = array_np_size - real_size  # 実際の情報量とndrrayの差分

        row = [ele_num, real_size, array_diff, array_np_diff, array_size, array_np_size]
        rows.append(row)

        # リアルタイム処理経過出力
        if num_by_100 >=1 and (idx % num_by_100)==0:
            print(f"{idx/num_by_100}% done.")

    # CSV出力
    folder_path = "research/memory/report/variables/"
    file_name = f"memory_{ele_num_max}_{step}.csv"
    file_path = folder_path + file_name
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    # PNG出力: メモリ量と差分ファイル
    folder_path = "research/memory/report/variables/"
    file_name_memory = f"memory_{ele_num_max}_{step}.png"  # メモリ量ファイル
    file_name_diff = f"diff_{ele_num_max}_{step}.png"  # 差分ファイル
    file_path_memory = folder_path + file_name_memory  
    file_path_diff = folder_path + file_name_diff
    # データを線ごとに分解
    ele_datas = [row[0] for row in rows]  # 横軸
    real_datas = [row[1] for row in rows]
    array_diff_datas = [row[2] for row in rows]
    ndarray_diff_datas = [row[3] for row in rows]
    array_datas = [row[4] for row in rows]
    ndarray_datas = [row[5] for row in rows]

    # ----------メモリ使用量ファイル----------
    # グラフ作成
    plt.figure(figsize=(10, 6))
    plt.plot(ele_datas, real_datas, label="実際の情報量")
    plt.plot(ele_datas, array_datas, label="配列のメモリ使用量")
    plt.plot(ele_datas, ndarray_datas, label="ndarrayのメモリ使用量")

    # グラフの装飾
    plt.title("メモリ使用量 vs 要素数", fontsize=16)
    plt.xlabel("要素数", fontsize=14)
    plt.ylabel("メモリ使用量", fontsize=10)
    plt.legend(fontsize=12)
    plt.grid(True)

    # 横軸,縦軸の区切りを10分割に変更
    max_y = max(max(array_datas), max(ndarray_datas))
    num_ticks = 10
    x_ticks = np.linspace(step, len(ele_datas), num_ticks, dtype=int)
    y_ticks = np.linspace(step, max_y, num_ticks, dtype=int)
    plt.xticks(x_ticks, fontsize=8)
    plt.yticks(y_ticks, fontsize=8)

    # ファイルに保存
    plt.savefig(file_path_memory, dpi=400)
    plt.close()

    # ----------差分ファイル----------
    # グラフ作成
    plt.figure(figsize=(10, 6))
    plt.plot(ele_datas, array_diff_datas, label="実際の情報量と配列のメモリ使用量の差分")
    plt.plot(ele_datas, ndarray_diff_datas, label="実際の情報量とndarrayのメモリ使用量の差分")

    # グラフの装飾
    plt.title("実際の情報量とメモリ使用量の差分 vs 要素数", fontsize=16)
    plt.xlabel("要素数", fontsize=14)
    plt.ylabel("実際の情報量とメモリ使用量の差分", fontsize=10)
    plt.legend(fontsize=12)
    plt.grid(True)

    # 横軸,縦軸の区切りを10分割に変更
    max_y = max(max(array_diff_datas), max(ndarray_diff_datas))
    num_ticks = 10
    x_ticks = np.linspace(step, len(ele_datas), num_ticks, dtype=int)
    y_ticks = np.linspace(step, max_y, num_ticks, dtype=int)
    plt.xticks(x_ticks, fontsize=8)
    plt.yticks(y_ticks, fontsize=8)

    # ファイルに保存
    plt.savefig(file_path_diff, dpi=400)
    plt.close()



if __name__ == "__main__":
    step = 1  # 100万
    ele_num_max = 100  # 1億
    get_array_memoy_relation(step, ele_num_max)