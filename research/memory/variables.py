"""


"""
import numpy as np
import csv


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
    ele = 0xffffffffffffffff  # 全ての要素は固定とする
    real_size = 64  # 実際の1要素(状態)のサイズは64bit
    array = []
    
    headers = ["要素数", "実際の情報量", "実際の情報量とarrayの差分", "実査愛の情報量とnp.ndrrayの差分", "array", "np.ndarray"]
    rows = [headers]
    
    for i in range(1, ele_num_max, step):
        
    
    
    