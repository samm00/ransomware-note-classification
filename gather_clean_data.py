import os
import json
import pandas as pd
import random
import re
import html2text
from markdown import markdown
import trafilatura
import json

NUM_FILES_TO_SAMPLE = 1  # 36

# init html2text
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True

data = {}
keys = []
for path, subdirs, files in os.walk("raw_data/prose"):
    for name in files:
        key = os.path.join(path, name)
        if name.endswith("txt"):
            keys.append(key)

for key in random.sample(keys, NUM_FILES_TO_SAMPLE):
    with open(key, "r", encoding="latin1") as f:
        words = f.read().split(" ")
        start_idx = random.randrange(len(words) - 750)
        data[key] = " ".join(
            words[start_idx : start_idx + 750]
        )  # get a random 750-word selection


em = pd.read_csv("raw_data/Translated_emails.csv").sample(
    NUM_FILES_TO_SAMPLE * 7
)  # data is smaller, so we want more of it
em = dict(zip(["em_" + str(id) for id in list(em["id"])], list(em["text"])))

data.update(em)


def get_text(urls):
    for url in urls:
        try:
            yield h.handle(trafilatura.fetch_url(url))
        except:
            yield None


btc = pd.read_csv("raw_data/bitcoin_news_articles.csv").sample(NUM_FILES_TO_SAMPLE * 3)  # Get more than needed, since not all will work
btc["link"] = [article for article in get_text(btc["link"])]
btc = btc.dropna().sample(NUM_FILES_TO_SAMPLE * 2)
btc = dict(zip(["btc_" + str(id) for id in list(btc["article_id"])], list(btc["link"])))

data.update(btc)

path = "raw_data/instructables/projects_"


def read_instructable_csv(name):
    return pd.read_csv(path + name).sample(
        NUM_FILES_TO_SAMPLE // 6
    )  # We want an eequal number of each 6 csv


diy = pd.concat(
    map(
        read_instructable_csv,
        [
            "circuits.csv",
            "cooking.csv",
            "craft.csv",
            "living.csv",
            "outside.csv",
            "workshop.csv",
        ],
    )
)
diy["Instructables-link"] = "https://www.instructables.com/" + diy["Instructables-link"]
diy["Instructables-link"] = list(get_text(diy["Instructables-link"]))
diy = dict(zip(["diy_" + str(id) for id in list(diy["Project-Title"])], list(diy["Instructables-link"])))

data.update(diy)

readme = {}
keys = []
for path, subdirs, files in os.walk("raw_data/READMEs_en"):
    for name in files:
        key = os.path.join(path, name)
        keys.append(key)

for key in random.sample(keys, NUM_FILES_TO_SAMPLE):
    with open(key, "r", encoding="latin1") as f:
        html = f.read()
        m = markdown(html)
        readme[key] = h.handle(html)

data.update(readme)

todo = pd.read_json("raw_data/todo.json")[["TaskTitle", "ListTitle"]]
# build todo lists from individual entries
todo = todo.groupby(["ListTitle"], as_index=False).agg({"TaskTitle": "\n".join})
todo["TaskTitle"] = todo["ListTitle"] + ":\n\n" + todo["TaskTitle"]
todo = dict(zip(["todo_" + str(id) for id in list(todo["ListTitle"])], list(todo["TaskTitle"])))

data.update(todo)

jrnl = pd.read_csv("raw_data/journal_entries.csv")["Answer"].sample(NUM_FILES_TO_SAMPLE * 7)
jrnl = dict(zip(["jrnl_" + str(id) for id in list(jrnl.index)], list(jrnl)))

data.update(jrnl)

resume = pd.read_csv("raw_data/resumes.csv").sample(NUM_FILES_TO_SAMPLE * 2)
resume = dict(zip(["resume_" + str(id) for id in list(resume.index)], resume["Resume_html"].apply(h.handle)))

data.update(resume)

path = 'raw_data/game_dialogue/'
torchlight = pd.read_csv(path+'torchlight_ii.csv')[['raw_text']].sample(NUM_FILES_TO_SAMPLE * 2).rename(columns={"raw_text": "text"})
torchlight['id'] = 'game_torchlight-' + torchlight.index.astype(str)
starwars = pd.read_csv(path+'star_wars.csv')[['text']].sample(NUM_FILES_TO_SAMPLE * 2)
starwars['id'] = 'game_starwars-' + starwars.index.astype(str)
elderscrolls = pd.DataFrame(json.load(open(path+'elder_scrolls.json')).values())[['text']].sample(NUM_FILES_TO_SAMPLE * 2)
elderscrolls['id'] = 'game_elderscrolls-' + elderscrolls.index.astype(str)
game = pd.concat([torchlight, starwars, elderscrolls])
game = dict(zip(list(game['id']), list(game['text'])))

data.update(game)

def sanitize(text):
    link = r"(https?:\/\/)?(www\.)?([\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+\.[\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+)+"
    try:
        text = re.sub(link, " REPLACEDLINK ", text)
    except:
        print(f"cannot replace link in:\t {text}")
    text = re.sub(r"<.+?>", "", text)
    text = re.sub(r"\u0000", "", text)
    text = re.sub(r"[\\/]", " ", text)
    text = re.sub(r"[^a-zA-Z\d\s@\.,!\?:;\']", "", text)
    text = re.sub(r"\s\s+", " ", text) # Normalize whitespaces to no more than once consecutively
    text = re.sub(r"\n\n+", "\n", text)
    text = re.sub(r"[^\s\.!:,\\/@;]{40,}", "", text)  # there are no words longer than 40 characters
    return text.strip()


data = {k: sanitize(v) for k, v in data.items()}

with open("data/non_malicious_data.json", "w") as f:
    json.dump(data, f, ensure_ascii=False)
