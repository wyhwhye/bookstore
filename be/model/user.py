import jwt
import time
import logging
import sqlite3 as sqlite
import pymongo
from be.model import error
from be.model import db_conn


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.user_col = self.conn['user']
        self.store_col = self.conn['store']

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            self.user_col.insert_one({
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal,
                "stores": [],
                "orders": []
            })
            # self.conn.execute(
            #    "INSERT into user(user_id, password, balance, token, terminal) "
            #    "VALUES (?, ?, ?, ?, ?);",
            #    (user_id, password, 0, token, terminal),
            # )
            # self.conn.commit()
        except pymongo.DuplicateKeyError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        # cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
        cursor = self.user_col.find_one({"user_id": user_id}, {"_id": 0, 'token': 1})
        # row = cursor.fetchone()
        if cursor is None:
            return error.error_authorization_fail()
        db_token = cursor['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        cursor = self.user_col.find_one({'user_id': user_id}, {'_id': 0, 'password': 1})
        # cursor = self.conn.execute(
        #     "SELECT password from user where user_id=?", (user_id,)
        #  )
        # row = cursor.fetchone()
        if cursor is None:
            return error.error_authorization_fail()

        if password != cursor['password']:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            # cursor = self.conn.execute(
            #    "UPDATE user set token= ? , terminal = ? where user_id = ?",
            #    (token, terminal, user_id),
            # )
            cursor = self.user_col.update_one({'user_id': user_id}, {'$set': {'token': token, 'terminal': terminal}})
            if cursor.modified_count == 0:
                return error.error_authorization_fail() + ("",)
            # self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            cursor = self.user_col.update_one({'user_id': user_id},
                                              {'$set': {'token': dummy_token, 'terminal': terminal}})
            # cursor = self.conn.execute(
            #    "UPDATE user SET token = ?, terminal = ? WHERE user_id=?",
            #    (dummy_token, terminal, user_id),
            # )
            if cursor.modified_count == 0:
                return error.error_authorization_fail()

            # self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            # cursor = self.conn.execute("DELETE from user where user_id=?", (user_id,))
            cursor = self.user_col.delete_one({'user_id': user_id})
            # if cursor.deleted_count == 1:
            # self.conn.commit()
            # else:
            if cursor.deleted_count != 1:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
            self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            # cursor = self.conn.execute(
            #    "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
            #    (new_password, token, terminal, user_id),
            # )
            cursor = self.user_col.update_one({'user_id': user_id}, {
                '$set': {'password': new_password, 'token': token, 'terminal': terminal}})

            if cursor.modified_count == 0:
                return error.error_authorization_fail()

            # self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def view_order_history(self, user_id: str, password: str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            orders = self.user_col.find_one(
                {'user_id': user_id},
                {"_id": 0, "orders": 1}
            )["orders"]

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", orders

    def search_books(self, store_id: str, title: str, tags: str, content: str):
        try:
            books_ite = b = self.store_col.find(
                {
                    "store_id": {"$regex": store_id},
                    "books.book_info.title": {"$regex": title},
                    "books.book_info.tags": {"$regex": tags},
                    "books.book_info.content": {"$regex": content},
                },
                {'_id': 0, "store_id": 1, "books.book_id": 1}
            )
            print(books_ite)
            books = []
            for b in books_ite:
                print(b)
                books.append(b)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", books
