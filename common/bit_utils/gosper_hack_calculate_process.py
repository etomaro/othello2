import csv
import os


def _get_patterns_by_gospers_hack(r: int):
    """
    5.1 固定長(b4bit)かつで1の数が固定のすべてのパターンを取得する(gosper's hack)
    計算の過程も含めて戻り値を作成する

    args:
        n: bit長でありnCrのn
        r: nCrのr
    retruns:
        bits: [
            1. 計算前の値,
            2. x &= MASK_64,
            3. u = x & -x,
            4. x + u,
            5. v = (x + u) & MASK_64,
            6. v ^ x,
            7. (v ^ x) & MASK_64,
            8. ((v ^ x) & MASK_64) >> 2,
            9. (((v ^ x) & MASK_64) >> 2) // u,
            10. ((((v ^ x) & MASK_64) >> 2) // u) | v
        ]
    """
    MASK_64 = (1 << 64) - 1  # 0xFFFF_FFFF_FFFF_FFFF

    def next_combination_64(x: int) -> int:
        datas = [x]
        # まず 64ビットとして x をマスクしておく
        x &= MASK_64
        datas.append(x)

        u = x & -x
        datas.append(u)
        datas.append(x + u)
        v = (x + u) & MASK_64
        datas.append(v)
        if v == 0:
            datas.extend([0,0,0,0,0])
            return datas
        
        # 下記の部分も適宜マスク
        datas.append(v ^ x)
        datas.append((v ^ x) & MASK_64)
        datas.append(((v ^ x) & MASK_64) >> 2)
        datas.append((((v ^ x) & MASK_64) >> 2) // u)
        datas.append(((((v ^ x) & MASK_64) >> 2) // u) | v)
        return datas

    if r == 0:
        yield 0
        return
    if r > 64:
        return

    bits = ((1 << r) - 1) & MASK_64
    yield ["", "", "", "", "", "", "", "", "", bits]  # 最初の戻り値
    bits = next_combination_64(bits)
    while bits[-1] != 0:
        yield bits
        bits = next_combination_64(bits[-1])

if __name__ == "__main__":

    # Gosper's hack計算過程をCSVに出力する(64C3)
    # 最初の5つと最後の4つを出力する。64C3の個数は41664
    keys = [
        "1. 計算前の値", 
        "2. x &= MASK_64",
        "3. u = x & -x",
        "4. x + u",
        "5. v = (x + u) & MASK_64",
        "6. v ^ x",
        "7. (v ^ x) & MASK_64",
        "8. ((v ^ x) & MASK_64) >> 2",
        "9. (((v ^ x) & MASK_64) >> 2) // u",
        "10. ((((v ^ x) & MASK_64) >> 2) // u) | v"
    ]
    headers = [
        "計算過程",
        "1つ目",
        "2つ目",
        "3つ目",
        "4つ目",
        "41662つ目",
        "41663つ目",
        "41664つ目",
    ]
    all_patterns = list(_get_patterns_by_gospers_hack(3))

    # create write datas
    write_datas = []
    for i in range(10):
        write_datas.append(
            [
                keys[i],
                format(all_patterns[0][i], "064b") if all_patterns[0][i] != "" else "",  # 1つ目の戻り値
                format(all_patterns[1][i], "064b") if all_patterns[1][i] != "" else "",  # 2つ目の戻り値
                format(all_patterns[2][i], "064b") if all_patterns[2][i] != "" else "",  # 3つ目の戻り値
                format(all_patterns[3][i], "064b") if all_patterns[3][i] != "" else "",  # 4つ目の戻り値
                format(all_patterns[41662-1][i], "064b") if all_patterns[41662-1][i] != "" else "",  # 41662つ目の戻り値
                format(all_patterns[41663-1][i], "064b") if all_patterns[41663-1][i] != "" else "",  # 41663つ目の戻り値
                format(all_patterns[41664-1][i], "064b") if all_patterns[41664-1][i] != "" else "",  # 41664つ目の戻り値
            ]
        )        

    # write
    folder_name = os.path.dirname(__file__)  + "gosper_hack_calculate_process_report"
    file_name = "gosper_hack_calculate_process.csv"
    file_path = folder_name + "/" + file_name
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(write_datas)

    # write2(41664個)
    write_datas = []
    for i, value in enumerate(all_patterns):
        write_datas.append([i+1, format(all_patterns[i][-1], "064b")])

    file_name = "gosper_hack_calculate_list.csv"
    file_path = folder_name + "/" + file_name
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(write_datas)
    