import csv


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
    while bits != 0:
        yield bits
        bits = next_combination_64(bits)

if __name__ == "__main__":

    # Gosper's hack計算過程をCSVに出力する(64C3)
    # 最初の5つと最後の4つを出力する。64C3の個数は41664
    count = 0
    datas = {}
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
        "1つ目",
        "2つ目"
    ]
    all_patterns = list(_get_patterns_by_gospers_hack(3))
    