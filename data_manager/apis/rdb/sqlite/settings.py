# DB path(.gitignoreの関係で拡張子は.sqlite3に統一すること)
TEST_DB_PATH = "data_manager/apis/rdb/sqlite/db/test_states.sqlite3"  # テスト用
DB_PATH = "data_manager/apis/rdb/sqlite/db/states.sqlite3"

# ※ 初期登録のみで書き換えしないことを注意する
# 1万件のデータ登録されたDB
TEST_DB_PATH_10000 = "data_manager/apis/rdb/sqlite/db/test_states_10000.sqlite3"
# 10万件のデータ登録されたDB
TEST_DB_PATH_100000 = "data_manager/apis/rdb/sqlite/db/test_states_100000.sqlite3"
# 100万件のデータ登録されたDB
TEST_DB_PATH_1million = "data_manager/apis/rdb/sqlite/db/test_states_1million.sqlite3"
# 1000万件のデータ登録されたDB
TEST_DB_PATH_10million = "data_manager/apis/rdb/sqlite/db/test_states_10million.sqlite3"
# 1億件のデータ登録されたDB
TEST_DB_PATH_100million = "data_manager/apis/rdb/sqlite/db/test_states_100million.sqlite3"
# 10億件のデータ登録されたDB
TEST_DB_PATH_1billion = "data_manager/apis/rdb/sqlite/db/test_states_1billion.sqlite3"
# 100億件のデータ登録されたDB
TEST_DB_PATH_10billion = "data_manager/apis/rdb/sqlite/db/test_states_10billion.sqlite3"

# 設定値
BATCH_SIZE = 10000000  # 1000万 

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
QUERY_STATES_GET_ALL = "SELECT black, white, player FROM states"

# トランザクション開始
QUERY_TRANSACTION_START = "BEGIN TRANSACTION"