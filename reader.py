from collections import namedtuple
from api.endpoint import Endpoint
import sys
import os


Article = namedtuple("Article", ["id", "title", "desc", "article"])


def parse(r):
    id      = r.json().get("id")
    title   = r.json().get("title")
    desc    = r.json().get("desc")
    article = r.json().get("article")
    article = Article(id, title, desc, article)
    return article


def pformat(article):
    text = f"""TITLE: {article.title}</br>
 ID    : {article.id}</br>
 DESC  : {article.desc}</br>
</br></br>
{article.article}"""
    return text


def write(article, text):
    fname = os.path.join("articles", f"{str(article.id)}.html")
    with open(fname, "w") as fhand:
        fhand.write(text)
    os.system(f"firefox {fname}")
    os.remove(fname)


def delete(article, flags):
    data  = f"ID: {str(article.id)}    FLAGS: {flags}\n"
    fname = os.path.join("articles", "delete.list.txt")
    with open(fname, "a") as fhand:
        fhand.write(data)


def review(article, text):
    print(f"{article.id}.html written to ./articles/")
    print("Please inspect article, and determine its quality.")
    os.system("reset")
    d = input("Delete article? [y/N]\n>>> ")
    if ("y" in d.lower()):
        flags = input("Take note of any prohibited terms:\n>>> ")
        delete(article, flags)
        print(f"{article.id} flagged for manual deletion.")


def main(m, n):
    endpoint = Endpoint()
    for id in range(m, n + 1):
        r = endpoint.get(id)
        if (r.status_code == 200):
            article = parse(r)
            text = pformat(article)
            write(article, text)
            review(article, text)


if __name__ == "__main__":
    try:
        m, n = int(sys.argv[1]), int(sys.argv[2])
    except (IndexError, ValueError):
        print("Integer range (minimum, maximum) required as cmd line args.")
        sys.exit(0)
    else:
        main(m, n)
