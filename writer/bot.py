from collections import OrderedDict
from collections import Counter

from transformers import pipeline
from datetime import datetime
import sqlite3
import random
import time
import sys


data = {"generations": 0, "lifetime iterations": 0, "curgen iterations": 0, 
        "fails": 0}


MIN = 500 # NOTE supposed to be 500
ARTISTS = [" Drake", " Eminem", " Dre", " Snoop",  " Tupac"]
BEATS   = [" trap beat", " trap banger", " banger", " beat", " sick beat",
           " trap beat", " trap beat", " trap beat", " wicked beat", 
           " sick trap beat", " wicked trap beat", " sick banger", 
           " wicked banger", " sick trap banger", " wicked trap banger", 
           " trap beat", " trap beat"]


class Article:


    REJECT = ["childhood", "world", "young", "my soul", "education", 
              " wood ", "india", "canada", "france", "ireland" "germany",
              "a&r"]


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
             "m not a producer", "certified", "private eye", "website",
             "ve no idea what I am doing", "school", " mom", " mother", 
             " camera", " pictures", r"i don't know much", "i dont know much",
             " interview", r"i didn't know how", "i didnt know how", "email",
             " create more people", " pic ", " in training", " sex", " indie", 
             " dad", " bother", " mother", " mom", " father", " sister", 
             " folk", " customer", " son", " daughter", " niece", " nephew",
             "i do not have a lot of experience", 
             "i don\'t have a lot of experience",
             "i dont have a lot of experience", "i do not write my own music",
             "i don\'t write my own music", "i dont write my own music",
             "i don\'t know", "i dont know", "i do not know", 
             "thats very interesting", "that\'s very interesting", 
             "that is very interesting", "thats really interesting",
             "that\'s really interesting", "that is really interesting", 
             " kill ", "@gmail", ".com", "@hotmail", ".net", ".org", " act",
             "example:", "dramer", "myspace", " tv ", " episode",
             ]

    REPLACE = [(" kid ", " rapper "), (" kids ", " rappers "), 
               (" rhythm guitar", " MPC"),
               (" lead guitar", " MPC"), (" bass guitar", " MPC"), 
               (" guitar", " MPC"),
               (" child", "rapper"), (" children", " rappers"),
               (" songwriter", " beat maker"), (" song writer", " beat maker"),
               (" song writing", " beat making"), 
               (" songwriting", " beat making"),
               (" musician", " music producer"),
               (" trap", " trap beat"), (" trap beat beat", " trap beat"),
               (" song", " trap beat"),
               (" beat", " trap beat"), (" trap trap beat", " trap beat"),
               (" Trap trap beat", " Trap beat"),
               (" music trap beat", " trap beat"),
               #(" the trap beats", " trap beats"), 
               #(" trap beat", BEATS),
               (" album", " mixtape"), (" an mixtape", " a mixtape"),
               (" cd", " mixtape"), (" band", " rap group"), (" MCss", " MCs"),
               (" a MCs", " MCs"), (" live gig show", " rap battle"),
               (" live concert show", " rap battle"),
               (" live show", " rap battle"), (" live concert", " rap battle"),
               (" gig", " rap battle"), (" concert", " rap battle"),
               #(" show", " rap battle"),
               (" the beatles", ARTISTS), (" the prodigy", ARTISTS),
               (" greatest hits", " fire"), (" rock star", " rap star"),
               (" 191", " 201"), (" 192", " 201"), (" 193", " 201"),
               (" 194", " 201"), (" 195", " 201"), (" 196", " 201"),
               (" 197", " 201"), (" 198", " 201"), (" 199", " 201"),
               (" 200", " 201"), (" singer", " MC"), (" a MC", " an MC"), 
               (" singing", " rapping"), (" sing ", " rap "), 
               (" sing.", " rap."), (" sing,", " rap,"), (" sing?", " rap?"),
               (" sing;", " rap;"), (" sing\\", " rap\\"), 
               (r' sing"', r' rap"'), (r" sing)", r" rap)"),
               (" human", " producer"), (" artist", " rapper"),
               (" an artist", " a rapper"), (" bass drum", " sick 808"),
               (" trap beat drummer", " trap beat maker"), 
               (" neighborhood", " hood"), (" an rapper", " a rapper"),
               (" karaoke performance", " rap battle"), 
               (" rap rap group", " rap group"), 
               (" drum trap beat", " drum beat"), 
               (" music festival", " rap battle"),]


    KEYWORDS = [" rap", " MPC", " beat", " producer", " mixtape", " MC",]


    def __init__(self):
        self._database = "articles/database.db"
        self.author    = "EleutherAI/gpt-neo-125M"
        self.title     = None
        self.desc      = None
        self.text      = None


    def _set_generator(self):
        generator = pipeline('text-generation', model = self.author)
        self._generator = generator


    def write(self, slug, test = None, max_length = 800, do_sample = True, 
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
                print(f"\n [GENERATION]"
                      f"[<< {str(data['generations']).zfill(5)} >>]"
                      f"[TIME]: {minutes} minutes. "
                      f"{data['curgen iterations']} of {data['lifetime iterations']}"
                      f" iterations.")
                print(f" This article iteration did not meet standard: {str(e)}")
                print(" Sleeping 10 seconds for garbage collection. Retrying.\n")
                time.sleep(10)
                continue

        self._compile()
        print(self.compiled_article.replace("</p><p>", "\n\n"))
        if not test:
            self._database_write()
        else:
            print("Skipping database write because testing.")
        data["generations"] += 1
        minutes = int((datetime.utcnow() - now).total_seconds() / 60)
        print(f" [SUCCESS] : [GENERATION][<< "
              f"{str(data['generations']).zfill(5)} >>][TIME]:"
              f" {minutes} minutes.")


    def _validate(self):
        text      = self.text.lower().split()
        text      = [t.rstrip(".").rstrip("?") for t in text]
        count     = Counter(text)
        relevance = count["beat"] + count["beats"]
        relevance += count["producer"] + count["studio"] + count["mixtape"]
        relevance += count["trap"] + count["music"] + count["rap"]
        relevance += count["rapper"] + count["rapping"] + count["raps"]
        relevance = round(relevance / len(text) * 100, 2)
        assert 1 <= relevance, f"only {relevance}% relevance to the topic."
        print(f" Article has {relevance}% topical relevance.")


    def _reshape(self, text, slug):
        self._super_filter(text)
        text = text[len(slug):].strip()
        text = ".".join(text.split(".")[:-1]) + "."
        assert len(text.split(" ")) >= MIN, (f"only {len(text.split(' '))} "
                                              "words (stage-1.)")
        text = self._replace(text)
        text = self._filter(text)
        text = self._duplicate_sentences(text)
        assert len(text.split(" ")) >= MIN, (f"only {len(text.split(' '))} "
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
            elif (word == " song") and (text.lower().find(" beat") != -1):
                continue
            text = text.replace(word.title(), replacement.title())
            text = text.replace(word, replacement)
        return text


    def _unique(self, text):
        t = text.lower()
        t = t.split(" ")
        t = [s.strip(".") for s in t if len(s.strip(".")) > 5]
        try:
            percent_unique = round((len(set(t)) / len(t)) * 100, 2)
            assert percent_unique >= 40, f"only {percent_unique}% unique."
        except ZeroDivisionError:
            assert False, f"only 0% unique." 


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

    
    def _make_title(self):
        sentences = self.text
        sentences = sentences.replace(",", " ")
        sentences = sentences.replace("?", " ")
        sentences = sentences.replace("!", " ")
        sentences = sentences.replace(r"(", " ")
        sentences = sentences.replace(r")", " ")
        sentences = sentences.split(".")
          
        results = []    
        for keyword in __class__.KEYWORDS:
            for sentence in sentences:
                if sentence.lower().count("i am a music producer"):               
                    continue
                elif sentence.lower().count("ixxxm a music producer"):
                    continue
                elif sentence.lower().count("i`m a music producer"):
                    continue
                elif sentence.lower().count("i am a producer"):
                    continue
                elif sentence.lower().count("ixxxm a producer"):
                    continue
                elif sentence.lower().count("i`m a producer"):
                    continue
                elif sentence.lower().count("i am a rapper"):
                    continue
                elif sentence.lower().count("ixxxm a rapper"):
                    continue
                elif sentence.lower().count("i`m a rapper"):
                    continue
                elif sentence.lower().count(keyword):
                    results.append(sentence)

        if not results:
            self.title = random.choice(sentences)
        else:
            self.title = min(results, key = lambda t: len(t))

        self.title = self.title.title()

        #input(f"stage-1: {self.title}")
        
        if 9 <= len(self.title.split(" ")):
            self.title = self.title.split(" ")
            if 15 <= len(self.title):
                center = len(self.title) // 3
                parts = [self.title[:center], self.title[center:center+center],
                         self.title[center+center:]]
            else:
                center = len(self.title) // 2
                parts = [self.title[:center], self.title[center:]]
            for keyword in __class__.KEYWORDS:
                for part in parts:
                    part = " ".join(part)
                    if part.lower().count(keyword):
                        self.title = part
                        break
                if (self.title == part):
                    break

        #input(f"stage-2: {self.title}")

        if isinstance(self.title, str):
            self.title = self.title.split(" ")

        while (self.title) and (len(self.title[-1]) <= 2):
            self.title = self.title[:-1]

        while 45 <= len(" ".join(self.title)):
            self.title = self.title[:-2]

        while (self.title) and (len(self.title[-1]) <= 2):
            self.title = self.title[:-1]
        
        self.title = " ".join(self.title)

        #input(f"stage-3: {self.title}")

        #self.title = self.title.rstrip(" And")
        #self.title = self.title.rstrip(" A")
        #self.title = self.title.rstrip(",")
        #self.title = self.title.rstrip(", ")
        #self.title = self.title.rstrip(" bee")

        self.title = self.title.lstrip("Of ")
        self.title = self.title.lstrip("And ")
        #self.title = self.title.lstrip("Talks ")
        #self.title = self.title.lstrip("Hen ")
        self.title = self.title.lstrip("By ")
        #self.title = self.title.lstrip("o ")
        #self.title = self.title.lstrip("his ")

        #input(f"stage-4: {self.title}")

        t = ""
        for e, word in enumerate(self.title.split(" ")):
            if ((not e) or (4 <= len(word))) or (word == "I") or (
                    word == "Rap") or (word == "CD"):
                t += word + " "
            else:
                t += word.lower() + " "
        self.title = t.rstrip(" ")

        #input(f"stage-5: {self.title}")

        replacements = [(" Down", " down"), (" Onto", " onto"),
                (" Over", " over"), (" From", " from"), 
                (" Past", " past"), (" Into", " into"),
                (" Upon", " upon"), (" Near", " near"),
                (" With", " with"), (" Than", " than"),
                (" That", " that"), (" Till", " till"),
                (" When", " when"), (" Once", " once"),
                (" This", " this"), (" That", " that")]
        for o, n in replacements:
            self.title = self.title.replace(o, n)

        #input(f"stage-6: {self.title}")

        try:
            while self.title.split(" ")[0][0].islower():
                self.title = self.title.split(" ")[1:]
                self.title = " ".join(self.title)
        except IndexError as e:
            raise AssertionError("Title creation failed.")

        self.title = self.title.replace("\"", "")

        try:
            self.title = self.title.split(" ")
            if self.title[-1][0].islower():
                self.title = " ".join(self.title)
                self.title += "..."
            else:
                self.title = " ".join(self.title)
        except IndexError as e:
            raise AssertionError("Title creation failed.")

        assert self.title, "Title creation failed."
            

    def _parse(self):
        self.text = self.text.replace('"', 'qqq')
        self.text = self.text.replace("”", "qqq")
        self.text = self.text.replace("“", "qqq")
        self.text = self.text.replace("'", "xxx")
        self.text = self.text.replace(r"`", "xxx")
        self.text = self.text.replace(r"’", "xxx")
        self._make_title()
        self.text = self.text.replace("xxx", "$$$")
        self.text = self.text.replace("Xxx", "$$$")
        self.text = self.text.replace("qqq", "###")
        self.text = self.text.replace("Qqq", "###")

        self.desc  = self.text[:80] + "..."
        self.text  = "<p>" + self.text.replace("\n\n", "</p><p>")
        self.text  = self.text.replace("<p></p>", "")
        if not self.text.endswith("."):
            if not self.text.endswith("?"):
                if not self.text.endswith("!"):
                    if not self.text.endswith(". "):
                        self.text += "."
        if self.text.endswith(". "):
            self.text = self.text.rstrip(" ")
        if not self.text.endswith("</p>"):
            self.text += "</p>"
        self.text = self.text.replace("..", ".")


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
