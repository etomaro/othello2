import hashlib
import sqlite3

from data_manager.apis.rdb.sqlite.settings import (
    QUERY_CREATE_STATES_TABLE, QUERY_STATES_CREATE_INDEX, QUERY_STATES_DELETE_INDEX,
    QUERY_STATES_BATCH_INSERT, QUERY_TRANSACTION_START, QUERY_STATES_INSERT,
    QUERY_STATES_GET, BATCH_SIZE, QUERY_STATES_GET_ALL
)
from data_manager.apis.rdb.sqlite.tools import initial_db



class States():
    def __init__(self, conn) -> None:
        """
        args:
          db_path: dbのパス  ※ テスト時は必ずテスト用のパスを使用すること
        """
        self.__conn = conn
        self.__cursor = self.__conn.cursor()
    
    def generate_hash(self, black: int, white: int, player: int) -> str:
        """
        正規化されたwhite, blackを基にハッシュ値を作成
        """
        state = f"{black}_{white}_{player}"
        return hashlib.sha256(state.encode()).hexdigest()
    
    def put(self, black: int, white: int, player: int, is_allowed_duplicate=False):
        """
        args:
          is_allowed_duplicate: 重複を許容する(例外をスローしない)
        """
        
        state_hash = self.generate_hash(black, white, player)

        try:
            self.__cursor.execute(
                QUERY_STATES_INSERT, (black, white, player, state_hash)
            )
            self.__conn.commit()
        
        except sqlite3.IntegrityError:
            # 重複のため追加されなかった
            if is_allowed_duplicate:
                # 重複を許可している場合は無視
                return
            else:
                raise
        
    def get(self, black: int, white: int, player: int) -> dict: 
        """
        returns:
            {
                "black": black,
                "white": white,
                "player": player,
                "hash": hash,
            }
        """
        hash_state = self.generate_hash(black, white, player)
        res = self.__cursor.execute(QUERY_STATES_GET, (hash_state,)).fetchone()
        
        # 取得できなかった場合例外をスロー
        if res is None:
            raise Exception(
                "can not get data"
                f"black: {black}"
                f"white: {white}"
                f"player: {player}"
                f"hash: {hash_state}"
            )
        else:
            return {
                # res[0]はid
                "black": res[1],
                "white": res[2],
                "player": res[3],
                "hash": res[4]
            }
    
    def get_all(self) -> list[dict]: 
        """
        returns:
        [
            {
                "black": black,
                "white": white,
                "player": player,
                "hash": hash,
            }
        ]
        """
        exp = []
        for i in range(5):
            exp_state_hash = self.generate_hash(i, i, i)
            exp.append(
                {
                    "black": i,
                    "white": i,
                    "player": i,
                    "hash": exp_state_hash
                }
            )
            # put
            self.put(i, i, i)
        
        # exec
        res = self.__cursor.execute(QUERY_STATES_GET_ALL).fetchall()
        
        result = []
        for data in res: 
            result.append(
                {
                    "black": data[1],
                    "white": data[2],
                    "player": data[3],
                    "hash": data[4]
                }
            )
        
        return result
    
    def bulk_insert(self, datas: list[tuple], chunk_size=BATCH_SIZE):
        """
        バッチ登録
        大量データを挿入する際にインデックスが存在すると挿入速度が低下する必要があるため
        一時的にインデックスを削除し、挿入後にインデックスを再作成を行う
        
        args:
          datas: [
              (black, white, player),
              ...
          ]
        """
        # hashを含めたデータにする
        states = [data + (self.generate_hash(data[0], data[1], data[2]), ) for data in datas]
        
        try:
            # インデックスの削除
            self.__cursor.execute(QUERY_STATES_DELETE_INDEX)
            
            # トランザクション開始
            self.__conn.execute(QUERY_TRANSACTION_START)
            
            for i in range(0, len(datas), chunk_size):
                # バッチ挿入
                self.__cursor.executemany(QUERY_STATES_BATCH_INSERT, states[i:i+chunk_size])
            
            # トランザクションコミット
            self.__conn.commit()
            
        except sqlite3.Error as e:
            # DB接続エラー
            self.__conn.rollback()
            raise
        except sqlite3.IntegrityError as ie:
            # IntegrityError
            self.__conn.rollback()
            raise
        except Exception as ex:
            self.__conn.rollback()
            raise
        finally:
            # いかなる時もこの処理を通る
            # インデックスの再作成
            self.__cursor.execute(QUERY_STATES_CREATE_INDEX)
            self.__conn.commit()
