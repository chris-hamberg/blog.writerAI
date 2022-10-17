from collections import namedtuple
import sqlite3


Article = namedtuple("Article", ["title", "author", "desc", "text"])


class Reader:


    def __init__(self):
        self.database = "articles/database.db"


    def read(self):
        sql = "SELECT * FROM article WHERE posted = False;"
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            q = cursor.execute(sql)
            article = q.fetchall()[0]
        article = Article(article[0], article[1], article[2], article[3])
        return article


    def update(self, article):
        sql  = """UPDATE article SET posted = True WHERE 
                  title = ? AND author = ? AND desc = ? AND text = ?;"""
        data = (article.title, article.author, article.desc, article.text)
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            q = cursor.execute(sql, data)
            connection.commit()


    def delete(self, article):
        sql  = "DELETE FROM article WHERE title = ? AND desc = ?;"
        data = (article.title, article.desc)
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            q = cursor.execute(sql, data)
            connection.commit()
