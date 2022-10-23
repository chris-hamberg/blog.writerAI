from pprint import pprint
from writer.ads import *
import requests
import time
import json


headers = {"Content-Type": "application/json"}
banner  = [BANNER_1, BANNER_2, BANNER_3]
url     = "https://metalheadmakesbeats.com/api/article/"
pw      = "3sBK60mtn9\l1i&CP*d_0GM.im06"
delim   = "</p> <p>"


def download_and_replace_ads(id):
    r = requests.get(url + str(id))
    assert int(r.status_code) == 200, r.status_code
    parts = r.json().get("article").split(delim)
    index = 0
    for i in range(len(parts)):
        if ((parts[i].count("banner")) and (index < len(banner))):
            parts[i] = str()
            index += 1
        if parts[i].count("Written by:"):
            parts[i] = parts[i].split("</p>")[-1]
    article = delim.join(parts)
    article = article.replace("<p></p>", "")
    article = article.replace("</p>  <p>", "</p><p>")
    article = article.replace("</p> <p>", "</p><p>")
    if not article.endswith("</p>"):
        article += "</p>"
    return article


def upload_replacement(article, id):
    data = {"article": article, "id": id, "password": pw}
    data = json.dumps(data)
    r = requests.patch(url, headers = headers, data = data)
    assert int(r.status_code) == 200


def main():

    for id in range(809, 890):
        try:
            article = download_and_replace_ads(id)
            print(f"retrived article id: {id}")
        except AssertionError as e:
            print(f"HTTP {str(e)}")
            continue
        try:
            upload_replacement(article, id)
        except AssertionError:
            print(f"FAILED ON ID: {id}")
        time.sleep(1)


if __name__ == "__main__":
    main()
