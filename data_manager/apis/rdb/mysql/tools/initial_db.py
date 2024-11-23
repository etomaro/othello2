import mysql.connector
from mysql.connector import errorcode
import mysql.connector.cursor
from data_manager.apis.rdb.mysql.query import (
    QUERY_DELETE_ALL_DATA_STATES, QUERY_CREATE_STATES_TABLE
)


def initial_db(db_settings: dict, is_delete: bool = False) -> None:
    """
    データ削除、テーブル作成、インデックス作成
    
    args:
        db_settings:
        {
            "host": host,
            "user": user,
            "password": password,
            "port": port,
            "db_name": db_name
        }
        is_delete:     
    """
    # データベース接続
    conn, cursor = connect_to_mysql(
        db_settings.get("host"), db_settings.get("user"), db_settings.get("password"),
        db_settings.get("port"), db_settings.get("db_name")
    )
    
    try:
        # テーブルが存在しない場合作成
        cursor.execute(QUERY_CREATE_STATES_TABLE)
        
        # インデックスが存在しない場合作成
        # uniqueのレコードは自動でインデックスを作成してくれる
        
        # データ削除
        if is_delete:
            _flash_data(cursor)
        
        conn.commit()
    except Exception:
        raise
    finally:
        cursor.close()
        conn.close()
    
def _flash_data(cursor) -> None:
    """
    データを削除(テーブルは削除しない)
    """
    cursor.execute(QUERY_DELETE_ALL_DATA_STATES)
    
def connect_to_mysql(
        host: str, user: str, password: str, port: str, db_name: str
    ) -> tuple[mysql.connector.connection, mysql.connector.cursor]:
    """接続用
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=db_name,
        )
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ユーザー名またはパスワードが間違っています。")
            raise
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("指定されたデータベースが存在しません。")
            raise
        else:
            print(err)
            raise
    
    except Exception as ex:
        print("Exception発生")
        print(ex)
        raise
