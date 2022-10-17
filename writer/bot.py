from transformers import pipeline
from pprint import pprint
from writer.ads import *
import sqlite3
import random
import time
import sys


class Article:


    FLAGS = ["fuck", " ass", "dumbass", "bitch", "damn", "pussy", "cunt",
             "dick", " tits", "boobs", " fag", "nigger", "nigga",
             "jew", "kkk", "nazi", "whore", "slut", " hoe",
             " cum", "clit", "douche", " kid", "amazon", "video",
             "movie", "hollywood", " pop", "country", "guitar",
             "bless", "heart", " cd", "twitter", "instagram", "1.", "1) ",
             "butt", "penis", "vagina", " cock", "balls", " band", "love",
             " photo", "google", "youtube", "microsoft", "facebook",
             "gig", "class", "hair", "blog", "concert", "1980", "aunt",
             " shit", "beatmix", "clothes", "naked", "beach", "http",
             "jimmy page", "90s", "80s", "loving", "girl", "sister",
             "b*tch", "kickass", "60s", "40 years", "50 years", "chicago bulls",
             "songwriter", "sunday", "monday", "tuesday", "wednesday",
             "thursday", "friday", "saturday", "january", "february",
             "march", "april", " may ", "june", "july", "august", "september",
             "october", "november", "december"
             ]


    def __init__(self):
        self._database = "articles/database.db"
        self.author = "EleutherAI/gpt-neo-125M"
        self.title  = None
        self.desc   = None
        self.text   = None


    def _set_generator(self):
        generator = pipeline('text-generation', model = self.author)
        self._generator = generator


    def write(self, slug, max_length = 500, do_sample = True, 
            temperature = 0.91):
        while True:
            self.text  = None
            self.title = None
            self.desc  = None
            self._set_generator()
            result = self._generator(slug, max_length = max_length, 
                    do_sample = do_sample, temperature = temperature)
            del self._generator
            text = result[0]["generated_text"]
            time.sleep(1)
            try:
                self._filter(text)
                break
            except AssertionError as e:
                del result, text
                print(f" Article did not meet standard: {str(e)}")
                print(" Sleeping 10 seconds for garbage collection.")
                time.sleep(10)
                continue
        self._parse(text, slug)
        self._compile()
        pprint(self.compiled_article)
        self._database_write()


    def _filter(self, text):
        length = len(text)
        newlines = text.count("\n\n")
        quotes   = text.count('\"')
        hyphens  = text.count("-")
        slashes  = text.count("\\")
        t        = text.lower()
        assert length   >= 1000,           f"only {length} characters."
        assert newlines <  5,              f"{newlines} double newlines."
        assert quotes   <  6,              f"{quotes} quotes."
        assert hyphens  <  5,              f"{hyphens} hyphens."
        assert slashes  <  5,              f"{slashes} back slashes."
        
        for flag in __class__.FLAGS:
            assert not t.count(flag),      f"prohibited term '{flag}'"

        t = t.split(" ")
        t = [s.strip(".") for s in t if len(s.strip(".")) > 4]
        percent_unique = round((len(set(t)) / len(t)) * 100, 2)
        assert percent_unique >= 50,       f"only {percent_unique}% percent unique."


    def _parse(self, text, slug):
        self.text  = text[len(slug):].strip()
        self.text  = self.text.replace('"', '\"')
        self.text  = self.text.replace("'", "")
        while not self.title:
            self.title = random.choice(self.text.split(".")).strip()
            self.title = self.title.title()
        self.title = " ".join(self.title.split(" ")[:7])
        self.desc  = self.text[:80] + "..."
        self.text  = ".".join(self.text.split(".")[:-1]) + "."
        self.text  = "<p>" + self.text.replace("\n\n", "</p> <p>")
        self.text  = self.text.replace("<p></p>", "")
        self.text  = self.text.replace(" beats", " trap beats")
        self.text  = self.text.replace("Beats ", "Trap beats ")
        self.text  = self.text.replace(" trap trap", " trap")
        self.text  = f"<p>Written by: {self.author} Robot.</p>" + self.text
        self.text  = self.text.split("</p> <p>")

        text = [self.text[0]]

        banners = [BANNER_1, BANNER_2, BANNER_3]

        index = 1
        position = 0
        minimum  = 350
        for i in range(len(self.text)):
            if ((2 + i) <= len(self.text)):
                index += 1
                if (0 != i):
                    text += [self.text[i]]
                if (minimum <= len(self.text[i])) and (position < len(banners)):

                    try:
                        t = self.text[i+1]
                        assert 500 <= len(str().join(self.text[i+1:]))
                    except (IndexError, AssertionError):
                        continue
                    else:
                        text += [banners[position]]
                        position += 1
                        minimum = 350

                elif (position < len(banners)):
                    minimum -= len(self.text[i])

        self.text = text + self.text[index:]
        self.text += [BANNER_END]

        self.text  = "</p> <p>".join(self.text)
        self.text = self.text + "</p>"


    def _compile(self):
        self.compiled_article = f"""
Title: {self.title}
Author: {self.author}
Description: {self.desc}

{self.text}
"""


    def _database_write(self):
        sql  = """INSERT INTO article (title, author, desc, text)
                  VALUES (?, ?, ?, ?);"""
        data = (self.title, self.author, self.desc, self.text)
        with sqlite3.connect(self._database) as connection:
            cursor = connection.cursor()
            q = cursor.execute(sql, data)
            connection.commit()
        self.title = None


if __name__ == "__main__":
    try:
        slug = sys.argv[1]
    except IndexError:
        print("argv slug required.")
        sys.exit(0)
    else:
        article = Article()
        result = article.write(slug)
