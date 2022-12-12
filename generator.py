from articles.reader import Reader
from api.endpoint import Endpoint
from writer.bot import Article
import time
import sys
import os


def main(n, slug, test):
    endpoint = Endpoint()
    reader   = Reader()
    counter  = 0
    errors   = 0
    while (counter < int(n)):

        article = Article()
        article.write(slug, test)

        if test:
            print("Skipping upload due to testing.")
            counter += 1
            continue
            
        data = reader.read()
        r = endpoint.post(data)
        print(f"\nHTTP {r.status_code}")
        del article
        if (r.status_code == 201) or (r.status_code == 200):
            reader.update(data)
            counter += 1
            print(f"Wrote {counter}/{n} articles. {errors} error(s).")
        else:
            reader.delete(data)
            errors += 1
            print(f"{r.json()}")
            print(f"Failed to write. {counter}/{n} articles written."
                  f" {errors} error(s).")
        if (counter < int(n)):
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
    
    try:
        main(n, slug, test)
    except KeyboardInterrupt:
        path = os.path.join("writer", "ACTIVE")
        if os.path.exists(path): os.remove(path)
