# DB path(.gitignoreの関係で拡張子は.sqlite3に統一すること)
TEST_DB_PATH = "data_manager/apis/rdb/sqlite/db/test_states.sqlite3"  # テスト用
DB_PATH = "data_manager/apis/rdb/sqlite/db/states.sqlite3"

# 設定値
BATCH_SIZE = 100000  # 10万 

# ---query---
# statesテーブル作成
QUERY_CREATE_STATES_TABLE = '''
    CREATE TABLE IF NOT EXISTS states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        black INTEGER NOT NULL,
        white INTEGER NOT NULL,
        player INTEGER NOT NULL,
        hash TEXT NOT NULL UNIQUE
    )
'''
# statesインデックス作成
QUERY_STATES_CREATE_INDEX = 'CREATE INDEX IF NOT EXISTS idx_hash ON states(hash)'
# statesインデックス削除
QUERY_STATES_DELETE_INDEX = 'DROP INDEX IF EXISTS idx_column_name;'
# states登録
QUERY_STATES_INSERT = "INSERT INTO states (black, white, player, hash) VALUES (?, ?, ?, ?)"
# statesバッチ挿入
QUERY_STATES_BATCH_INSERT = '''
    INSERT INTO states (black, white, player, hash)
    VALUES (?, ?, ?, ?);
'''
# states get
QUERY_STATES_GET = "SELECT * FROM states WHERE hash = ?"
# get all
QUERY_STATES_GET_ALL = "SELECT * FROM states"

# トランザクション開始
QUERY_TRANSACTION_START = "BEGIN TRANSACTION"