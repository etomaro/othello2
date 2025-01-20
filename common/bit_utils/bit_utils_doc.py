"""
ビット操作に関する実装型のドキュメント

---仕様系---
1.1 指定桁以下のビットをすべて1、指定桁より上をすべて0
1.2. 無限長でのビット反転(~x)
1.3. 固定長でのビット反転(~x & mask)
1.4. -x

---基本演算系---
2.1 &
2.2 |
2.3 xor 
2.4 左シフト
2.5 右シフト
2.6 1の数をカウント

---文字列出力---
3.1 0bをつけずに出力
3.2 固定長のbitとして0bをつけずに出力

---小技---
4.1 奇数・偶数判定
4.2 最も下位の1ビットを取り出す(x & -x)

---大技---
5.1 固定長かつで1の数が固定のすべてのパターンを取得する(gosper's hack)

"""

def _get_1_under_the_digit(digit: int) -> int:
    """
    1. 指定桁以下のビットをすべて1、指定桁より上をすべて0
    
    ロジック
      最終的な値+1の状態を生成して-1をすることで取得する
    
    ex: digit=3, return=0b0111
    
    args:
      digit: 指定桁
    """
    return 1<<(digit+1) - 1
  
def _get_bit_reverse(value: int) -> int:
    """
    2. 無限長でのビット反転(~x)

    まずpythonでの数値は無限長ビット扱いになる。
    例えば10進数で3は2進数では0b010や0b10でpythonだとかけるが
    データ上だとどちらも000....00010

    ビット反転を行うと
    111...11101

    ビット反転したものをpython上で2進数で出力すると
    print(bin(~x)) -> "-0b100"と出力される
    ※ 混乱を招く原因だが負の値をpythonで2進数文字出力をすると"-" + "絶対値"の形で出力される
    ※ pythonは2の補数(~x+1)を用いているため「0b111...11101」は「-4」となる。「4」は「0b100」のため「-0b100」と出力されている

    ※ 2の補数の性質上、最上位ビットが1の場合は負の値    
    """
    return ~value

def _get_bit_reverse_limited(value: int, mask_ndigit) -> int:
    """
    3. 固定長でのビット反転(~x & mask)

    数値としてではなくビットとして使用する際に使用する考え方

    0b1101 -> 0b0010としたい場合に使用する
    正確には「0b1101」は「0b000...1101」,「0b0010」は「0b000...0010」のため~
    xとしても「0b111...1101」となるため「0b0010」とはならない
    
    ビット反転したものに使用するビット幅のすべてが1のマスクと&を取ることで実現する
    ex: 0b1101 -> ビット反転 -> 0b111..1101 -> 0b1111のマスクと& -> 0b1101

    args:
      value: 値
      mask_ndigit: ビット反転する最大桁数(ex: mask_ndigit=4の場合マスクは0b1111)
    """
    mask = 2**mask_ndigit -1  # mask_ndigitが2の場合0b100 - 1 -> 0b11
    return mask & ~value

def _get_negative_value(value: int) -> int:
    """
    4. -x
    
    コンピューターで負の値を表現する方法を考える
    どの方法だとしてもnbit固定長の場合表現できる絶対値の個数は2^(n-1)個
    
    1. 絶対値表現
        n固定値で数値を扱う場合、n番目を+or-を扱う。
          n       | n-1  n-2 1  |
        0 or 1    | 数値の絶対値 |
         
    2. 1の補数
        ※ なぜ1の補数というか
        ※ 補数とは: n進数の数に加算すると1桁上がる数の最小値。2進数の場合,最低でも+2をすると1桁上がるため2進数の補数は2で「2の補数」という
        
        「1の補数方式」は、“全ビットが1の状態”(例えば8ビットなら 1111 1111-255)を基準にして「その値との差をとる」ことによって負数を表現する。
        -> ビット反転した形になる
        
        0101 0101の場合
        1010 1010が負の値と表現する。最上位のビットは正負の判定になる
        
        デメリット: 0000 0000と1111 1111がともにゼロになる(0と-0が混在する)
        
    3. 2の補数
        ビット反転+1の方法で負の値を表現する(=1の補数に1を加算したもの)
        common/bit_utils/2の補数.xlsxに記載

        定義: -x = ~x + 1

        メリット: 負の値を使用しても加算ができる
      
    args:
      value: 値
    """
    return ~value + 1
  
def _get_and(x: int, y: int) -> int:
    """
    2.1 &

    ※ andは使用できない

    負の値の検討
    -5: 0b111..011
    -4: 0b111..100
    
    -5と-4を&すると「-8」になる

    -8: 0b111..1000
    -> 確かにandすると-8になる
    """
    return x & y 

def _get_or(x: int, y: int) -> int:
    """
    2.2 |

    ※ orは使用できない

    負の値の検討
    -5: 0b111..011
    -4: 0b111..100

    -5と-4をorすると5になる

    -1: 0b111..111
    -> orすると確かに-1になる
    """
    return x | y 

def _get_bit_count(value: int) -> int:
    """
    2.6 1の数をカウント

    python3.10以上だとbit_count()が使用できる
    未満だとbin(x).count("1")が使用できるが遅い
    """
    return value.bit_count()

def _get_xor(x: int, y: int) -> int:
    """
    3. xor(^)

    どちらのみが1を1にする
    """
    return x ^ y

def _get_str_without_0b(value: int) -> int:
    """
    3.1 0bをつけずに出力
    """
    return format(value, "b")

def _get_str_without_0b_limited(value: int, digit: int) -> int:
    """
    3.2 固定長のbitとして0bをつけずに出力(0で置換する)

    [ex]
    x = 0b1010
    format(x, "08b"): "00001010"

    args:
      value: 値
      digit: 何桁の固定長とするか
      rep_value: 何の値で埋めるか
    """
    return format(value, f"0{digit}b")

def _get_judge_odd_even(value: int) -> int:
    """
    4.1 奇数・偶数判定

    奇数の場合、最下位ビットは1
    偶数の場合、最下位ビットは0
    を利用して判定
    """
    if value & 0b1:
        return True 
    else:
        return False
    
def _get_underest_one(value: int) -> int:
    """
    4.2 最も下位の1ビットを取り出す(x & -x)
    
    [ex]
    x = 0b0110
    result = 0b10

    ロジック
    x: 0b00..0110
    -x: 0b11..001 + 0b00..1 = 0b11..010
    result: 0b010
    """
    return value & -value

def _get_patterns_by_gospers_hack(r: int):
    """
    5.1 固定長(b4bit)かつで1の数が固定のすべてのパターンを取得する(gosper's hack)

    args:
        n: bit長でありnCrのn
        r: nCrのr
    """
    MASK_64 = (1 << 64) - 1  # 0xFFFF_FFFF_FFFF_FFFF

    def next_combination_64(x: int) -> int:
        # まず 64ビットとして x をマスクしておく
        x &= MASK_64

        u = x & -x
        v = (x + u) & MASK_64
        if v == 0:
            return 0
        
        # 下記の部分も適宜マスク
        return ((((v ^ x) & MASK_64) >> 2) // u) | v

    if r == 0:
        yield 0
        return
    if r > 64:
        return

    bitmask = ((1 << r) - 1) & MASK_64
    while bitmask != 0:
        yield bitmask
        bitmask = next_combination_64(bitmask)
