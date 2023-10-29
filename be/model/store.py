import logging
import os
import sqlite3 as sqlite
import pymongo


class Store:
    # database: str

    def __init__(self, db_path):
        # self.database = os.path.join(db_path, "be.db")
        # self.init_tables()
        client = pymongo.MongoClient("mongodb://localhost:27017/")  # 连接mongodb
        db = client.bookstore  # 切换到bookstore数据库

        # 设置唯一索引
        book_col = db['book']
        book_col.create_index([("isbn", 1)], unique=True)

        user_col = db['user']
        user_col.create_index([("user_id", 1)], unique=True)

        store_col = db['store']
        store_col.create_index([("store_id", 1)], unique=True)

        order_col = db['order']
        order_col.create_index([("order_id", 1)], unique=True)

    # def init_tables(self):
    #
    #     try:
    #         conn = self.get_db_conn()
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user ("
    #             "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
    #             "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    #         )
    #
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user_store("
    #             "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
    #         )
    #
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS store( "
    #             "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
    #             " PRIMARY KEY(store_id, book_id))"
    #         )
    #
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order( "
    #             "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
    #         )
    #
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order_detail( "
    #             "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
    #             "PRIMARY KEY(order_id, book_id))"
    #         )
    #
    #         conn.commit()
    #     except sqlite.Error as e:
    #         logging.error(e)
    #         conn.rollback()
    #
    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    client = pymongo.MongoClient("mongodb://localhost:27017/")  # 连接mongodb
    database_instance = client.bookstore  # 切换到bookstore数据库

    return database_instance
