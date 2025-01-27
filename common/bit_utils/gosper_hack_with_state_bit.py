

def get_60_c_r_by_gosper_hack_with_state_bit(r: int):
    """
    Gosper's Hackの応用でGosper's Hackで求めたそれぞれに指定されたビット長に変換かつ、固定のビットを立てる

    [ex]
    64bitの内(index=0~63)7bitのみを「1」とする全パターンを取得する。
    ただし、index=27,28,35,36は固定で1とする

    1. まずindex=27,28,35,36を除いたindex=0~63の内3bitを立てる全パターンを取得する(=60C3=34220通り)
    2. 求めたパターンをそれぞれ64ビットに変換してindex=27,28,35,36を立てる
    2.1. 「1.」で求めたものを3分割する
    2.2. それぞれ最終的な64bitの形にシフトして分割ごとのマスクを取る
    2.3. index=27,28,35,36のマスクを求める
    2.4. 「2.2.」「2.3.」のorで結合する

    [オセロのindex]
    63 62 61 60 59 58 57 56
    55 54 53 52 51 50 49 48
    47 46 45 44 43 42 41 40
    39 38 37 36 35 34 33 32
    31 30 29 28 27 26 25 24
    23 22 21 20 19 18 17 16
    15 14 13 12 11 10  9  8
    7  6  5  4  3  2  1  0

    [63C3のインデックス]
    59 58 57 56 55 54 53 52
    51 50 49 48 47 46 45 44
    43 42 41 40 39 38 37 36
    35 34 33 △ △ 32 31 30    
    29 28 27 △ △ 26 25 24
    23 22 21 20 19 18 17 16
    15 14 13 12 11 10  9  8
    7  6  5  4  3  2  1  0

    [ex]
    (1.  )0000,0000,0000,0001,0000,0000,0001,0000,0001,0000,0001,0000,0000,0000,0000,0000
    ※ 下記移行インデックスはオセロのインデックスを指す
    (2.1.)
        a1 = index63~37
        a2 = index34~29
        a3 = index26~0
    (2.2.)
        b1 = (x<<4) と index63~37とのマスク
        b2 = (x<<2) と index34~29とのマスク
        b3 =      x と index26~0とのマスク
    (2.3. ), (2.4. )
        ※ 省略
 
    args:
      r: nCrのr, generationの値と同値
    """
    MASK_60 = (1 << 60) - 1  # 0xFFF_FFFF_FFFF_FFFF

    def next_combination_60(x: int) -> int:
        # まず 64ビットとして x をマスクしておく
        x &= MASK_60

        u = x & -x
        v = (x + u) & MASK_60
        if v == 0:
            return 0
        
        # 下記の部分も適宜マスク
        return ((((v ^ x) & MASK_60) >> 2) // u) | v
    
    def add_with_state_value(x: int) -> int:
        """
        2. 求めたパターンをそれぞれ64ビットに変換してindex=27,28,35,36を立てる
        """
        a1 = (x<<4) & 0xffffffe000000000  # index63~37
        a2 = (x<<2) & 0x00000007e0000000  # index34~29
        a3 = x & 0x0000000007ffffff  # index26~0
        z = 0x0000001818000000  # index=27,28,35,36のマスク
        return a1 | a2 | a3 | z

    # 高速化のためコメントアウト。r=0 or 64より上の値で呼ばないこと
    # if r == 0:
    #     yield 0
    #     return
    # if r > 64:
    #     return

    bitmask = ((1 << r) - 1) & MASK_60
    while bitmask != 0:
        yield add_with_state_value(bitmask)
        bitmask = next_combination_60(bitmask)
