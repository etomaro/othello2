"""
世代ごとの状態数を算出する
"""
from env_v2.anality.not_batch import not_batch
from env_v2.anality.batch4 import run as run_v4
from env_v2.anality.batch5 import run as run_v5
from env_v2.anality.batch2 import batch as batch_for_anality
from env_v2.anality.batch import batch


if __name__ == "__main__":
    # not batch
    # not_batch(8)
    
    # batch
    run_v5(3)
    # for i in range(0, 10):
    #     print("-----------start-----------")
    #     run(i)
    #     print(f"{i} done")
