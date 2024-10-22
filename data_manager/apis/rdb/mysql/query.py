# statesテーブルを全削除
QUERY_DELETE_ALL_DATA_STATES = "truncate table states;"

QUERY_CREATE_STATES_TABLE = """
    CREATE TABLE IF NOT EXISTS states (
        id INT PRIMARY KEY AUTO_INCREMENT,
        black BIGINT NOT NULL,
        white BIGINT NOT NULL,
        player INT NOT NULL,
        hash VARCHAR(255) NOT NULL UNIQUE
    );
"""
