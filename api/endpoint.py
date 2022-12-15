import requests
import time
import json
import os


class Endpoint:


    def __init__(self):
        self.url      = "https://metalhead-makes-beats.onrender.com"
        self.password = "3sBK60mtn9\l1i&CP*d_0GM.im06"
        self.headers  = {"Content-Type": "application/json"}


    def post(self, article):
        url, retries, t = f"{self.url}/api/article/", 10, 1.01
        data = {
            "title"   : article.title,
            "author"  : article.author,
            "desc"    : article.desc,
            "article" : article.text,
            "password": self.password}
        while retries:
            try:
                r = requests.post(url, headers = self.headers,
                        data = json.dumps(data))
                return r
            except requests.exceptions.ConnectionError:
                print(f"ConnectionError: sleeping {t} seconds.")
                time.sleep(t)
                t = t**2
                retries -= 1


    def get(self, id):
        url = f"{self.url}/api/article/{id}"
        r = requests.get(url)
        return r
