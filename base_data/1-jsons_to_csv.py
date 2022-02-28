import pandas as pd
from os import walk
import json

extractpath = "/home/martin/dev/scrape-grund/data/"

fn = []

for (dirpath, dirnames, filenames) in walk(extractpath):
    fn.extend(filenames)
    break

li = []

for f in fn:
    if f[-4:] == "json":
        wp = extractpath + f

        with open(extractpath + f, 'r') as dat:
            data=dat.read()

        obj = json.loads(data)

        for a in obj['articles']:
            if a['idx'] != 0:
                t = a['text'].encode("utf8")
                if len(t) > 0:
                    li.append( t.decode('utf8'))

df = pd.DataFrame(li, columns=['Text'])
df.to_csv(r'all_articles_in_text.csv', index = False)
