
import pymongo
from be.model import error
from be.model import db_conn
import uuid


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.store_col = self.conn['store']
        self.user_col = self.conn['user']
        self.order_col = self.conn['order']

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_dict: dict,
        stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            book = {
                "book_id": book_id,
                "book_info": book_dict,
                "stock_level": stock_level
            }
            self.store_col.update_one(
                {"store_id": store_id},
                {"$push": {"books": book}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.store_col.update_one(
                {"store_id": store_id, "books.book_id": book_id},
                {"$inc": {"books.$.stock_level": add_stock_level}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.store_col.insert_one({
                "store_id": store_id,
                "user_id": user_id,
                "books": []
            })
            self.user_col.update_one({'user_id': user_id},
                                     {'$push': {'stores': store_id}})
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def deliver_goods(self,
                      user_id: str,
                      store_id: str,
                      order_id: str
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            # if not self.store_id_exist(store_id):
            #     return error.error_non_exist_store_id(store_id)

            order = self.order_col.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            status = order['status']
            if status == "待支付":
                return 521, {"请先支付"}
            elif status == "待收货" or status == "已完成":
                return 522, {"已发货"}

            self.order_col.update_one(
                {"order_id": order_id},
                {"$set": {"status": "待收货"}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
