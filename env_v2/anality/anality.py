"""
世代ごとの状態数を算出する
"""
from env_v2.anality.not_batch import not_batch
from env_v2.anality.batch import batch


if __name__ == "__main__":
    # not batch
    # not_batch(8)
    
    # batch
    # batch(9)
    for i in range(10, 20):
        batch(i)
