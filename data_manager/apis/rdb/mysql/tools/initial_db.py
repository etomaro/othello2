import mysql.connector
from mysql.connector import errorcode
from data_manager.apis.rdb.mysql.query import (
    QUERY_DELETE_ALL_DATA_STATES
)


def initial_db(db_settings: dict, is_delete: bool = False) -> mysql.connector.connection:
    """
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
    conn = connect_to_mysql(
        db_settings.get("host"), db_settings.get("user"), db_settings.get("password"),
        db_settings.get("port"), db_settings.get("db_name")
    )
    
    # データ削除
    if is_delete:
        _flash_data(conn)
    
    return conn
    

def _flash_data(conn: mysql.connector.connection) -> None:
    """
    データを削除(テーブルは削除しない)
    """
    cursor = conn.cursor()
    cursor.execute(QUERY_DELETE_ALL_DATA_STATES)
    cursor.close()
    
def connect_to_mysql(
        host: str, user: str, password: str, port: str, db_name: str
    ) -> mysql.connector.connection:
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
        print("MySQLに接続しました。")
        return conn
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
        


def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
        print(f"データベース '{db_name}' を作成しました。")
    except mysql.connector.Error as err:
        print(f"データベース作成中にエラーが発生しました: {err}")
        exit(1)



