import pymongo

# 连接到MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.bookstore
order_col = db['order']

# 使用Change Stream监听删除操作
pipeline = [{'$match': {'operationType': 'delete'}}]
with order_col.watch(pipeline) as stream:
    for change in stream:
        print(change['documentKey'])

# # 保持监听活动
# while True:
#     pass
