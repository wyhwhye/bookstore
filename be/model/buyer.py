import pymongo
import uuid
import json
from be.model import db_conn
from be.model import error
import datetime


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.store_col = self.conn['store']
        self.user_col = self.conn['user']
        self.order_col = self.conn['order']

    def new_order(self, user_id: str, store_id: str, books: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            user = self.user_col.find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)

            store = self.store_col.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            purchases = []
            for book in books:
                book_id = book[0]
                count = book[1]
                book = self.store_col.find_one(
                    {"store_id": store_id, "books.book_id": book_id},
                    {"books.$": 1}
                )
                book = book['books'][0]
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                stock_level = book['stock_level']
                price = json.loads(book['book_info'])['price']
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                self.store_col.update_one(
                    {"store_id": store_id, "books.book_id": book_id, "books.stock_level": {"$gte": count}},
                    {"$inc": {"books.$.stock_level": -count}}
                )
                purchases.append({"book_id": book_id, "count": count, "price": price})

            self.order_col.insert_one({
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "books": purchases,
                "status": "待支付",
                "TTL": datetime.datetime.utcnow()
            })

            order_id = uid

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""

        except BaseException as e:
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order = self.order_col.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            if order['status'] != "待支付":
                return error.error_already_paid(order_id)  # 已支付的订单

            buyer_id = order['user_id']
            store_id = order['store_id']

            if buyer_id != user_id:
                return 401, "Authorization fail"

            user = self.user_col.find_one({"user_id": buyer_id})
            if user is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user['balance']
            if password != user['password']:
                return error.error_authorization_fail()

            seller = self.store_col.find_one({"store_id": store_id})
            if seller is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = seller['user_id']

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            total_price = 0
            for item in order['books']:
                count = item['count']
                price = item['price']
                total_price += int(price) * count

            print("total_price: ", total_price)
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            self.user_col.update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )

            self.order_col.update_one(
                {"order_id": order_id},
                {"$set": {"TTL": None, "status": "待发货"}}
            )

            # self.order_col.delete_one({"order_id": order_id})

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user = self.user_col.find_one({"user_id": user_id})
            if user is None:
                return error.error_authorization_fail()
            if user['password'] != password:
                return error.error_authorization_fail()

            self.user_col.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive_order(self,
                      user_id: str,
                      password: str,
                      order_id: str
    ):
        try:
            user = self.user_col.find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id)
            if password != user['password']:
                return error.error_authorization_fail()

            order = self.order_col.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            status = order['status']
            if status == "已完成":
                return 523, {"已收货"}
            elif status == "待发货" or status == "待支付":
                return 524, {"请等待快递送出"}

            self.order_col.update_one(
                {"order_id": order_id},
                {"$set": {"status": "已完成"}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self):
        pass
