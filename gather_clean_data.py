import os
import json
import pandas
import random
import trafilatura
import re

data = {}
keys = []
for path, subdirs, files in os.walk('clean_data/prose'):
    for name in files:
        key = os.path.join(path, name)
        if name.endswith('txt'):
            keys.append(key)

for key in random.sample(keys, 40):
    with open(key, 'r', encoding='latin1') as f:
        data[key] = ' '.join(f.read().split(' ')[:500])


em = pandas.read_csv('/home/sam/Documents/hacs479/clean_data/Translated_emails.csv').sample(150)
em = dict(zip(['em_' + str(id) for id in list(em['id'])], list(em['text'])))

data.update(em)

def get_text(urls):
    for url in urls:
        try:
            yield trafilatura.extract(trafilatura.fetch_url(url))
        except:
            yield None

btc = pandas.read_csv('/home/sam/Documents/hacs479/clean_data/bitcoin_news_articles.csv').sample(40)
btc['link'] = [article for article in get_text(btc['link'])]
btc = btc.dropna()
btc = dict(zip(['btc_' + str(id) for id in list(btc['article_id'])], list(btc['link'])))

data.update(btc)

diy = pandas.read_csv('/home/sam/Documents/hacs479/clean_data/instructables/projects_circuits.csv').sample(40)
diy['Instructables-link'] = 'https://www.instructables.com/' + diy['Instructables-link']
diy['Instructables-link'] = list(get_text(diy['Instructables-link']))
diy = dict(zip(['diy_' + str(id) for id in list(diy['Project-Title'])], list(diy['Instructables-link'])))

data.update(diy)

def sanitize(text):
    link = r'(https?:\/\/)?(www\.)?([\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+\.[\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+)+'
    try:
        text = re.sub(link, ' REPLACEDLINK ', text)
    except:
        print(text)
    text = re.sub(r'<.+?>', '', text)
    text = re.sub(r'\u0000', '', text)
    text = re.sub(r'[\\/]', ' ', text)
    text = re.sub(r'[^a-zA-Z\d\s@\.,!\?:;\']', '', text)
    text = re.sub(r'\s\s+', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    text = re.sub(r'[^\s\.!:,\\/@;]{40,}', '', text)
    return text.strip()

data = {k: sanitize(v) for k, v in data.items()}

with open('clean_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii = False)