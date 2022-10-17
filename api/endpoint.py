import requests
import json
import os


class Endpoint:


    def __init__(self):
        self.url      = "https://metalhead-makes-beats.onrender.com"
        self.password = "3sBK60mtn9\l1i&CP*d_0GM.im06"
        self.headers  = {"Content-Type": "application/json"}


    def post(self, article, test):
        if test:
            url = "http://127.0.0.1:5000/api/article/"
        else:
            url = f"{self.url}/api/article/"
        data = {
            "title"   : article.title,
            "author"  : article.author,
            "desc"    : article.desc,
            "article" : article.text,
            "password": self.password}
        r = requests.post(url, headers = self.headers, data = json.dumps(data))
        return r

