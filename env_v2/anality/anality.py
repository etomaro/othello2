"""
世代ごとの状態数を算出する
"""
from env_v2.anality.not_batch import not_batch
from env_v2.anality.batch2 import batch as batch_for_anality
from env_v2.anality.batch import batch


if __name__ == "__main__":
    # not batch
    # not_batch(8)
    
    # batch
    batch(10)
    # for i in range(2, 10):
    #     print("-----------start-----------")
    #     batch(i)
    #     print(f"{i} done")
