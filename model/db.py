# app/model/db.py
# import sqlite3
import pysqlite3 as sqlite3

DB_PATH = "database/transfermarkt.db"


class SQLiteConnector:
    def __init__(self):
        self.conn = None

    def __has_params(self, params):
        if not params:
            raise ValueError("Params must be set for batch execution")

    def __connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row

    def __close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, sql, params=None, batch=False):
        try:
            self.__connect()
            cursor = self.conn.cursor()

            if batch:
                self.__has_params(params)
                cursor.executemany(sql, params)
            else:
                cursor.execute(sql, params or [])

            self.conn.commit()

            return {"success": True, "message": f"Rows affected: {cursor.rowcount}"}

        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": str(e)}

        finally:
            self.__close()

    def get_data(self, sql, params=None, as_dict=False):
        try:
            self.__connect()
            cursor = self.conn.cursor()
            cursor.execute(sql, params or [])
            rows = cursor.fetchall()

            if as_dict:
                return [dict(r) for r in rows]

            print(f"get_data:\n{rows}")

            return rows

        except Exception as e:
            return {"success": False, "message": str(e)}

        finally:
            self.__close()

    def execute_script(self, sql):
        try:
            self.__connect()
            cursor = self.conn.cursor()
            cursor.executescript(sql)
            self.conn.commit()
            return {"success": True, "message": "Script executed successfully"}

        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": str(e)}

        finally:
            self.__close()
