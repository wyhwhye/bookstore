import pymongo

# 连接到MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.bookstore
order_col = db['order']
store_col = db['store']

# 使用Change Stream监听删除操作
pipeline = [{'$match': {'operationType': 'delete'}}]
with order_col.watch(pipeline) as stream:
    for change in stream:
        # print(change['documentKey'])
        order = change['documentKey']
        store_id = order["store_id"]
        for book in order['books']:
            store_col.update_one(
                {"store_id": store_id, "books.book_id": book["book_id"]},
                {"$inc": {"books.$.stock_level": book["count"]}}
            )

