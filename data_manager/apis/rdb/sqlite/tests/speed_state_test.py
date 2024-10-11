"""
データ登録・取得のスピード比較
時間がかかりそうなものはファイルを分ける
"""
import csv 
import time
import os

from common.create_test_state_data import create_data
from data_manager.apis.rdb.sqlite.states import States
from data_manager.apis.rdb.sqlite.tools.initial_db import initial_db
from data_manager.apis.rdb.sqlite.settings import TEST_DB_PATH


BASE_FOLDER = os.path.dirname(__file__)
FILE_PATH = BASE_FOLDER + "/" + "reports/speed_state_test.csv"
HEADER = ["件数", "バッチ件数", "登録時間", "読み取り時間"]


def run():
  """1万-1000万
  1. 件数: 1万, バッチ: 1万
  2. 件数: 10万, バッチ: 1万
  3. 件数: 10万, バッチ: 10万
  4. 件数: 100万, バッチ: 1万
  5. 件数: 100万, バッチ: 10万
  6. 件数: 100万, バッチ: 100万
  7. 件数: 1000万, バッチ: 1万
  8. 件数: 1000万, バッチ: 10万
  9. 件数: 1000万, バッチ: 100万
  10. 件数: 1000万, バッチ: 1000万
  """
  settings = [
    (10000, 10000),  # 1. 件数: 1万, バッチ: 1万
    (100000, 10000),  # 2. 件数: 10万, バッチ: 1万
    (100000, 100000),  # 3. 件数: 10万, バッチ: 10万
    (1000000, 10000),  # 4. 件数: 100万, バッチ: 1万
    (1000000, 100000),  # 5. 件数: 100万, バッチ: 10万
    (1000000, 1000000),  # 6. 件数: 100万, バッチ: 100万
    (10000000, 10000),  # 7. 件数: 1000万, バッチ: 1万
    (10000000, 100000),  # 8. 件数: 1000万, バッチ: 10万
    (10000000, 1000000),  # 9. 件数: 1000万, バッチ: 100万
    (10000000, 10000000),  # 10. 件数: 1000万, バッチ: 1000万
  ]
  with open(FILE_PATH, "w") as f:
      writer = csv.writer(f)
      writer.writerow(HEADER)
      for state_num, batch_num in settings:
        # DB初期化
        conn = initial_db(TEST_DB_PATH, is_delete=True)
        api = States(conn)
        
        # 登録データ作成
        data = create_data(state_num)
        
        # 登録
        start_time_write = time.time()
        api.bulk_insert(data, batch_num)
        write_time = time.time() - start_time_write
        del data
        formatted_time_write = time.strftime('%H時間%M分%S秒', time.gmtime(write_time))
        print(f"register done. state_num: {state_num}, batch_num: {batch_num}")
        
        # 読み取り
        start_time_read = time.time()
        read_data = api.get_all()
        read_time = time.time() - start_time_read
        del read_data 
        formatted_time_read = time.strftime('%H時間%M分%S秒', time.gmtime(read_time))
        print(f"read done. state_num: {state_num}, batch_num: {batch_num}")
        
        # CSV出力
        writer.writerow([state_num, batch_num, formatted_time_write, formatted_time_read])

def run_many(state_num: int, batch_num: int, file_path: str):
  """
  時間がかかるため1つの計測で1つのファイルを作成する
  """
  with open(file_path, "w") as f:
      writer = csv.writer(f)
      writer.writerow(HEADER)
      
      # DB初期化
      conn = initial_db(TEST_DB_PATH, is_delete=True)
      api = States(conn)
      
      # 登録データ作成
      data = create_data(state_num)
      
      # 登録
      start_time_write = time.time()
      api.bulk_insert(data, batch_num)
      write_time = time.time() - start_time_write
      del data
      formatted_time_write = time.strftime('%H時間%M分%S秒', time.gmtime(write_time))
      print(f"register done. state_num: {state_num}, batch_num: {batch_num}")
      
      # 読み取り
      start_time_read = time.time()
      read_data = api.get_all()
      read_time = time.time() - start_time_read
      del read_data 
      formatted_time_read = time.strftime('%H時間%M分%S秒', time.gmtime(read_time))
      print(f"read done. state_num: {state_num}, batch_num: {batch_num}")
      
      # CSV出力
      writer.writerow([state_num, batch_num, formatted_time_write, formatted_time_read])
              

if __name__ == "__main__":
    # 1万-1000万
    # run()
    
    # 1億
    state_num = 100000000 
    file_path = BASE_FOLDER + "/" + "reports/speed_state_test_100million.csv"
    run_many(state_num, state_num, file_path)
    
    # 10億
    # state_num = 1000000000
    # file_path = BASE_FOLDER + "/" + "reports/speed_state_test_billion.csv"
    # run_many(state_num, state_num, file_path)
        
    