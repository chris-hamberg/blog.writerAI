from articles.reader import Reader
from api.endpoint import Endpoint
from writer.bot import Article
import time
import sys


def main(n, slug, test):
    endpoint = Endpoint()
    reader   = Reader()
    counter  = 0
    errors   = 0
    while (counter < int(n)):
        article = Article()
        article.write(slug)
        data = reader.read()
        r = endpoint.post(data, test)
        print(f"\nHTTP {r.status_code}")
        del article
        if (r.status_code == 201) or (r.status_code == 200):
            if not test:
                reader.update(data)
            else:
                reader.delete(data)
            counter += 1
            print(f"Wrote {counter}/{n} articles. {errors} error(s).")
        else:
            reader.delete(data)
            errors += 1
            if not test:
                print(f"{r.json()}")
                print(f"Failed to write. {counter}/{n} articles written."
                      f" {errors} error(s).")
        if ((not test) and (counter < int(n))):
            del data, r
            print(f"Sleeping 1 minute(s).\n")
            time.sleep(60)


if __name__ == "__main__":
    try:
        test = None
        n, slug, test = sys.argv[1], sys.argv[2], sys.argv[3:]
        if test:
            test = test[0]
    except IndexError:
        print("Number of articles to post and slug are required args.")
        sys.exit(0)
    else:
        main(n, slug, test)
