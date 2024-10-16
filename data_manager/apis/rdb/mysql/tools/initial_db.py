import mysql.connector
from mysql.connector import errorcode

from data_manager.apis.rdb.mysql.settings import (
    HOST, USER, PASSWORD
)



def connect_to_mysql(host, user, password):
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )
        print("MySQLに接続しました。")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ユーザー名またはパスワードが間違っています。")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("指定されたデータベースが存在しません。")
        else:
            print(err)
    return None


def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
        print(f"データベース '{db_name}' を作成しました。")
    except mysql.connector.Error as err:
        print(f"データベース作成中にエラーが発生しました: {err}")
        exit(1)



