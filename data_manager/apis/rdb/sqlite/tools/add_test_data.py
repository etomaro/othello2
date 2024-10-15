"""
大量件数のデータ登録に時間がかかるためtoolを用意
"""

import random
import os
import time
import csv
from datetime import datetime

from data_manager.apis.rdb.sqlite.states import States 
from data_manager.apis.rdb.sqlite.tools.initial_db import initial_db
from data_manager.apis.rdb.sqlite.settings import (
    TEST_DB_PATH, TEST_DB_PATH_10000, TEST_DB_PATH_100000,
    TEST_DB_PATH_1million, TEST_DB_PATH_10million, TEST_DB_PATH_100million,
    TEST_DB_PATH_1billion, TEST_DB_PATH_10billion
)

BASE_FOLDER = os.path.dirname(__file__)
FILE_PATH = BASE_FOLDER + "/" + "reports/PREFIX_REPORT_FILE.csv"
HEADER = [
    "件数目",
    "バッチ当たりの登録合計時間",
    "インデックスの削除時間",
    "インデックスの作成時間",
    "トランザクション開始時間",
    "インザート時間",
    "インザートコミット時間",
    "インデックス作成コミット時間",
    "合計経過時間",
]


def create_data(state_num: int) -> list[tuple]:
    """スピード比較用にデータ作成
    
    登録するデータ
      1. 黒石: 0x0-0x1111111111111111
      2. 白石: 0x0-0x1111111111111111
      3. player: 0 or 1
      
    1000万件のデータを作成するのに19s
    1億: 3m10s
    10億: 31m40s
    100億: 6h 
    
    args:
      state_num: 登録する件数
    returns:
      create_data: 登録するデータ
    """
    print("データ作成開始")
    lower_bound = 0x0
    upper_bound = 0x1111111111111111
    
    data = [
        (random.randint(lower_bound, upper_bound),
         random.randint(lower_bound, upper_bound),
         random.randint(0, 1)
         ) for _ in range(state_num)]
    
    print("データ作成終了")
    return data

def add_data(db_path: str, state_num: int, prefix_report_file: str) -> None:
    """
    DBにデータを登録する
    ※ 初期登録のみで書き換えしないことを注意する
    """
    # DBが存在する場合はデータが登録されているとみなして何もしない
    if os.path.exists(db_path):
        return 
    
    conn = initial_db(db_path, is_delete=True)
    api = States(conn)
    
    # 1000万ずつ登録する(1億以上ではOOMが発生したため)
    batch_num = 10000000

    full_batch = state_num // batch_num  # 1000万登録する回数
    remainder = state_num % batch_num  # 1000万未満の登録するデータ数
    
    try:
      file_path = FILE_PATH.replace("PREFIX_REPORT_FILE", prefix_report_file)
      with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        
        # トータル時間
        total_time = 0
        
        for i in range(full_batch):
            data = create_data(batch_num)
            start_batch_time = time.time()  # バッチ当たりの開始時間
            
            time_index_delete, time_index_create, time_transaction_start,\
                time_insert, time_commit_insert, time_commit_index_create =\
                api.bulk_insert(data, batch_num, debug=True)
            
            batch_time = time.time() - start_batch_time
            total_time += batch_time
            
            """CSV出力
            "件数目",
            "バッチ当たりの登録合計時間",
            "インデックスの削除時間",
            "インデックスの作成時間",
            "トランザクション開始時間",
            "インザート時間",
            "インザートコミット時間",
            "インデックス作成コミット時間",
            "合計経過時間",
            """
            num_process = (i+1) * batch_num
            
            batch_time_str = time.strftime('%H時間%M分%S秒', time.gmtime(batch_time))
            time_index_delete_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_index_delete))
            time_index_create_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_index_create))
            time_transaction_start_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_transaction_start))
            time_insert_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_insert))
            time_commit_insert_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_commit_insert))
            time_commit_index_create_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_commit_index_create))
            total_time_str = time.strftime('%H時間%M分%S秒', time.gmtime(total_time))
            
            writer.writerow(
                [
                    str(num_process), batch_time_str,
                    time_index_delete_str,
                    time_index_create_str,
                    time_transaction_start_str,
                    time_insert_str,
                    time_commit_insert_str,
                    time_commit_index_create_str,
                    total_time_str,
                ]
            )
            
            print(f"[tmp] add data. {num_process}")
            
            del data
            
        if remainder > 0:
            data = create_data(remainder)
            start_batch_time = time.time()  # バッチ当たりの開始時間
            
            time_index_delete, time_index_create, time_transaction_start,\
                time_insert, time_commit_insert, time_commit_index_create =\
                api.bulk_insert(data, batch_num, debug=True)
            
            batch_time = time.time() - start_batch_time
            total_time += batch_time
            
            batch_time_str = time.strftime('%H時間%M分%S秒', time.gmtime(batch_time))
            time_index_delete_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_index_delete))
            time_index_create_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_index_create))
            time_transaction_start_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_transaction_start))
            time_insert_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_insert))
            time_commit_insert_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_commit_insert))
            time_commit_index_create_str = time.strftime('%H時間%M分%S秒', time.gmtime(time_commit_index_create))
            total_time_str = time.strftime('%H時間%M分%S秒', time.gmtime(total_time))
            
            writer.writerow(
                [
                    str(state_num), batch_time_str,
                    time_index_delete_str,
                    time_index_create_str,
                    time_transaction_start_str,
                    time_insert_str,
                    time_commit_insert_str,
                    time_commit_index_create_str,
                    total_time_str,
                ]
            )
            
            del data
    except Exception as ex:
        print(f"データ作成失敗\n{ex}")
        # 失敗した場合DB削除
        os.remove(file_path)
        
        
def add_test_data():
    """テスト用データを登録する
    1. 1万件
    2. 10万件
    3. 100万件
    4. 1千万件
    5. 1億件
    6. 10億件
    7. 100億件
    
    5:30ごろから登録
    """
    settings = [
    #   (10000, TEST_DB_PATH_10000, "10000"),
    #   (100000, TEST_DB_PATH_100000, "100000"),
    #   (1000000, TEST_DB_PATH_1million, "1million"),
    #   (10000000, TEST_DB_PATH_10million, "10million"),
      (100000000, TEST_DB_PATH_100million, "100million"),
    #   (1000000000, TEST_DB_PATH_1billion, "1billion"),
    #   (10000000000, TEST_DB_PATH_10billion, "10billion"),
    ]
    
    settings = [
        (
            100000000,
            "data_manager/apis/rdb/sqlite/db/test_states_100million_by_100000.sqlite3",
            "100million_by_100000"
        )
    ]
    for state_num, db_path, prefix_report_file in settings:
        print(f"---start add data---")
        add_data(db_path, state_num, prefix_report_file)
        print(f"add data: {state_num}")
        
if __name__ == "__main__":
    start_time = time.time()
    # データ登録
    add_test_data()
    print(f"計測時間: {time.time() - start_time}")