"""
世代ごとの状態数を算出する
"""
from env_v2.anality.not_batch import not_batch
from env_v2.anality.batch2 import batch


if __name__ == "__main__":
    # not batch
    # not_batch(8)
    
    # batch
    # batch(12)
    for i in range(1, 10):
        print("-----------start-----------")
        batch(i)
        print(f"{i} done")
