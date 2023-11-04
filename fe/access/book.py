import os
import sqlite3 as sqlite
import random
import pymongo
import base64
import simplejson as json


class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
             self.book_db = self.db_l
        else:
             self.book_db = self.db_s

        # self.book_db = "mongodb://localhost:27017/"

        #client = pymongo.MongoClient("mongodb://localhost:27017/")  # 连接mongodb
        #db = client.bookstore  # 切换到bookstore数据库
        #self.books_col = db['book']

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        #conn = pymongo.MongoClient(self.book_db)
        cursor = conn.execute("SELECT count(id) FROM book")
        #books_col = conn['books']
        row = cursor.fetchone()
        

        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        #conn = pymongo.MongoClient(self.book_db)
        #books_col = conn['books']
        #cursor = self.books_col.find({},
         #                           {"_id": 0,
         #                            "id": 1,
         #                            "title": 1,
         #                            "author": 1,
         #                            "publisher": 1,
         #                            "original_title": 1,
         #                            "translator": 1,
         #                            "pub_year": 1,
         #                            "pages": 1,
         #                            "price": 1,
         #                            "currency_unit": 1,
         #                            "binding": 1,
         #                            "isbn": 1,
         #                            "author_intro": 1,
         #                            "book_intro": 1,
         #                            "content": 1,
         #                            "tags": 1,
         #                            "picture": 1}).sort('id', pymongo.ASCENDING).skip(start).limit(size)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?",
            (size, start),
         )
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)

            books.append(book)
            # print(tags.decode('utf-8'))
            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
