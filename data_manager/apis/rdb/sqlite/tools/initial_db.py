"""
指定されたSqlite DBを作成する
"""
import sqlite3
import os


def initial_db(db_path: str, is_delete=False) -> sqlite3.Connection:
    """Sqliteに接続する
    args:
      db_path: dbのパス
      is_delete: DBを削除
    returns:
      カーソルオブジェクト
    """
    # DBの削除
    if is_delete and os.path.exists(db_path):
        os.remove(db_path)
    
    # データベースに接続（DBが存在しない場合は自動的に作成される）
    conn = sqlite3.connect(db_path)
        
    try:
        # カーソルオブジェクトを作成
        cursor = conn.cursor()
        
        # TODO: 型は考慮する必要がある
        """テーブルの作成
        id: id
        black: 黒のボード
        white: 白のボード
        player: プレイヤーID
        hash: black,white,playerのハッシュ値
              ※ 複合キーにすると遅いのでハッシュ値で1keyにすることで速度改善
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                black INTEGER NOT NULL,
                white INTEGER NOT NULL,
                player INTEGER NOT NULL,
                hash TEXT NOT NULL UNIQUE
            )
        ''')

        # 変更を保存
        conn.commit()
        
        return conn
            
    except Exception:
        # 接続を閉じる
        conn.close()
        raise 
    

    
    