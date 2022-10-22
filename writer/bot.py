try:
    from writer.ads import *
except ModuleNotFoundError:
    from ads import *

from collections import OrderedDict
from collections import Counter

from transformers import pipeline
from datetime import datetime
from pprint import pprint
import sqlite3
import random
import time
import sys


data = {"generations": 0, "lifetime iterations": 0, "curgen iterations": 0, 
        "fails": 0}


class Article:


    REJECT = [" childhood", " world", " young", " my soul", " education",]


    FLAGS = ["fuck", " ass", "dumbass", "bitch", "damn", "pussy", "cunt", 
             "dick", " tits", "boobs", " fag", "nigger", "nigga", "jew", "kkk", 
             "nazi", "whore", "slut", " hoe", " cum", "clit", "douche", 
             "amazon", "video", "movie", "hollywood", " pop", "country", 
             "bless", "heart", "twitter", "instagram", "1", "2", "3", "4", "5", 
             "6", "7", "8", "9", "10 ", "11", "12", "13", "14", "15", "16", "17",
             "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28",
             "29", "30", "31", "32", "33", "34", "35", "36", "37", "mymusic",
             "butt", "penis", "vagina", " cock", "balls", "love", " photo", 
             "google", "youtube", "microsoft", "facebook", "class", "hair", 
             "blog", "aunt", " shit", "beatmix", "clothes", "naked", "beach", 
             "http", "jimmy page", "90s", "80s", "20s", "30s", "40s", "50s",
             "70s", "loving", "girl", "sister",
             "b*tch", "60s", "40 years", "50 years", "chicago bulls", "sunday", 
             "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", 
             "january", "february", "march", "april", " may ", "june", "july", 
             "august", "september", "october", "november", "december", 
             "sound track", "soundtrack", "wife", "my name", " string", " amp", 
             "nashville", ".html", "25 years", " i am a beginner", 
             " i am just a beginner", "m a beginner", "m just a beginner", 
             " afraid", " dance", " money", "m not very good", "m not good",
             " blues", "m not as good", "Chris Brown", "1:", "2:", "3:", "4:",
             "5:", "6:", "7:", "8:", "9:", "10:", "11:", "amateur", "portrait",
             "ve never", "i have never", " i never", " i haven\'t done",
             "i havent done", " i have not done", "ve not done", "sony",
             "camcorder", " shoot", " garage", "m not a music producer",
             "m not a producer", "certified", "private eye", "website",]

    REPLACE = [(" kid", " rapper"), (" kids", " rappers"), (" guitar", " MPC"), 
               (" child", "rapper"), (" children", " rappers"),
               (" songwriter", " beat maker"), (" song writer", " beat maker"),
               (" song writing", " beat making"), 
               (" songwriting", " beat making"),
               (" musician", " music producer"), (" song", " trap beat"),
               (" beat", " trap beat"), (" trap trap beat", " trap beat"),
               (" Trap trap beat", " Trap beat"),
               (" music trap beat", " trap beat"),
               #(" the trap beats", " trap beats"), 
               (" album", " mixtape"), (" an mixtape", " a mixtape"),
               (" cd", " mixtape"), (" band", " MCs"), (" MCss", " MCs"),
               (" a MCs", " MCs"), (" live gig show", " rap battle"),
               (" live concert show", " rap battle"),
               (" live show", " rap battle"), (" live concert", " rap battle"),
               (" gig", " rap battle"), (" concert", " rap battle"),
               (" show", " rap battle"),
               (" the beatles", [" Drake", " Eminem", " Dre", " Snoop", 
                   " Tupac"]),
               (" greatest hits", " fire"), (" rock star", " rap star"),
               (" 191", " 201"), (" 192", " 201"), (" 193", " 201"),
               (" 194", " 201"), (" 195", " 201"), (" 196", " 201"),
               (" 197", " 201"), (" 198", " 201"), (" 199", " 201"),
               (" 200", " 201"), (" singer", " rapper"), 
               (" singing", " rapping"), (" sing ", " rap"), 
               (" sing.", " rap."), (" sing,", " rap,"), (" sing?", " rap?"),
               (" sing;", " rap;"), (" sing\\", " rap\\"), 
               (r' sing"', r' rap"'), (r" sing)", r" rap)"),]


    def __init__(self):
        self._database = "articles/database.db"
        self.author    = "EleutherAI/gpt-neo-125M"
        self.title     = None
        self.desc      = None
        self.text      = None


    def _set_generator(self):
        generator = pipeline('text-generation', model = self.author)
        self._generator = generator


    def write(self, slug, max_length = 800, do_sample = True, 
            temperature = 0.91):
        data["curgen iterations"] = 0
        now = datetime.utcnow()
        while True:
            data["lifetime iterations"] += 1
            data["curgen iterations"] += 1
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
                self._reshape(text, slug)
                self._parse()
                self._validate()
                break
            except (AttributeError, AssertionError) as e:
                del result, text
                minutes = int((datetime.utcnow() - now).total_seconds() / 60)
                print(f" {data['curgen iterations']} <[CURGEN"
                      f" ITERATIONS]> of {data['lifetime iterations']}"
                      f" <[ITERATIONS]> across {data['generations']}"
                       " <[ARTICLE GENERATIONS]>")
                print(f" [GENERATION {data['generations']}]"
                      f"[TIME]: {minutes} minutes.")
                print(f" This article iteration did not meet standard: {str(e)}")
                print(" Sleeping 10 seconds for garbage collection. Retrying.\n")
                time.sleep(10)
                continue

        self._compile()
        pprint(self.compiled_article)
        self._embed_ads()
        self._database_write()
        data["generations"] += 1
        minutes = int((datetime.utcnow() - now).total_seconds() / 60)
        print(f" [GENERATION {data['generations']}][TIME]: {minutes} minutes.")


    def _validate(self):
        text      = self.text.lower().split()
        text      = [t.rstrip(".").rstrip("?") for t in text]
        count     = Counter(text)
        relevance = count["beat"] + count["beats"]
        relevance += count["producer"] + count["studio"] + count["mixtape"]
        relevance += count["trap"] + count["music"] + count["rap"]
        relevance += count["rapper"] + count["rapping"] + count["raps"]
        relevance = round(relevance / len(text) * 100, 2)
        assert 1 <= relevance, "only {relevance}% relevance to the topic."
        print(f" Article has {relevance}% topical relevance.")


    def _reshape(self, text, slug):
        self._super_filter(text)
        text = text[len(slug):].strip()
        text = ".".join(text.split(".")[:-1]) + "."
        assert len(text.split(" ")) >= 500, (f"only {len(text.split(' '))} "
                                              "words (stage-1.)")
        text = self._replace(text)
        text = self._filter(text)
        text = self._duplicate_sentences(text)
        assert len(text.split(" ")) >= 500, (f"only {len(text.split(' '))} "
                                              "words (stage-2.)")
        text = self._format(text)
        self._unique(text)
        self.text = text


    def _super_filter(self, text):
        for flag in __class__.REJECT:
            if text.lower().find(flag) != -1:
                assert False, (f"Article rejected for containing the "
                               f"term '{flag.lstrip()}'.")


    def _duplicate_sentences(self, text):
        ordered_set = OrderedDict()
        text = text.split(".")
        for sentence in text:
            ordered_set[sentence] = None
        text = ".".join(ordered_set.keys())
        return text


    def _replace(self, text):
        for word, replacement in __class__.REPLACE:
            if isinstance(replacement, list):
                replacement = random.choice(replacement)
            if (word == " song") and (text.lower().find("trap beat") != -1):
                continue
            elif (word == " song") and (text.lower().find("beat") != -1):
                continue
            text = text.replace(word.title(), replacement.title())
            text = text.replace(word, replacement)
        return text


    def _unique(self, text):
        t = text.lower()
        t = t.split(" ")
        t = [s.strip(".") for s in t if len(s.strip(".")) > 5]
        percent_unique = round((len(set(t)) / len(t)) * 100, 2)
        assert percent_unique >= 40, f"only {percent_unique}% percent unique."


    def _filter(self, text):
        text, temp = text.split("."), []
        for sentence in text:
            if sentence.count("-") > 3:    continue
            elif sentence.count("\\") > 3: continue
            for flag in __class__.FLAGS:
                if sentence.lower().count(flag.lower()):
                    break
            else:
                temp.append(sentence)
        return ".".join(temp)


    def _format(self, text):
        text, stri, queue = text.split("\n\n"), "", []
        n = random.randint(500, 800)
        for i in range(len(text)):
            queue.append(text[i])
            temp = " ".join(queue)
            if (len(temp) > n) and (len(" ".join(text[i+1:])) > n):
                stri += temp + "\n\n"
                queue.clear()
                n = random.randint(250, 500)
            elif (len(temp) > n) and (len(" ".join(text[i+1:])) <= n):
                stri += temp + " "
                i += 1
                break
        text = " ".join(text[i:])
        stri += text
        return stri
        

    def _parse(self):
        self.text  = self.text.replace('"', '\"')
        self.text  = self.text.replace("'", "")
        while not self.title:
            self.title = random.choice(self.text.split(".")).strip()
            self.title = self.title.title()
            self.title = max(self.title.split(","), key = lambda t: len(t))
        self.title = " ".join(self.title.split(" ")[:random.randint(5, 8)])
        self.desc  = self.text[:80] + "..."
        self.text  = "<p>" + self.text.replace("\n\n", "</p> <p>")
        self.text  = self.text.replace("<p></p>", "")
        #self.text  = f"<p>Written by: {self.author} Robot.</p>" + self.text


    def _embed_ads(self):
        temp = str()
        delim = "</p> <p>"
        text = self.text.split(delim)
        banners = [BANNER_1, BANNER_2, BANNER_3]
        if 4 <= len(text):
            for i in range(3):
                temp += text[i] + delim + banners[i] + delim
            temp += delim.join(text[3:])
        elif 3 <= len(text):
            for i in range(2):
                temp += text[i] + delim + banners[i] + delim
            temp += delim.join(text[2:])
        elif 2 <= len(text):
            temp = text[0] + delim + banners[0] + delim + text[1]
        elif 1 <= len(text):
            temp = delim.join(text)
        self.text = temp


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
