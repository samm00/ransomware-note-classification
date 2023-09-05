import os
import json
import pandas as pd
import random
import re
import html2text
from markdown import markdown
import trafilatura
import json

NUM_FILES_TO_SAMPLE = 42

# init html2text
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True

def get_text(urls: "list[str]"):
    '''
    Get text from url to webpage

    urls: list of urls to fetch text from

    returns: list of texts from webpages, with None used if 
    '''

    for url in urls:
        try:
            yield h.handle(trafilatura.fetch_url(url))
        except:
            yield None

# Init dictinary of all data
data = {}

## ## ###
# Prose #
### ## ##

keys = []
for path, subdirs, files in os.walk("raw_data/prose"):
    for name in files:
        key = os.path.join(path, name)
        if name.endswith("txt"):
            keys.append(key)

prose = {}
for key in random.sample(keys, NUM_FILES_TO_SAMPLE):
    with open(key, "r", encoding="latin1") as f:
        words = f.read().split(" ")
        start_idx = random.randrange(len(words) - 1500)
        prose['prose_' + key.split('/')[-1][:-4]] = " ".join(
            words[start_idx : start_idx + 1500]
        )  # get a random 1500-word selection

data.update(prose)

## ### ###
# Emails #
### ### ##

em = pd.read_csv("raw_data/Translated_emails.csv").sample(NUM_FILES_TO_SAMPLE * 10)  # data is smaller, so we want more of it
em = dict(zip(["em_" + str(id) for id in list(em["id"])], list(em["text"])))

data.update(em)


## ### ## ### ##
# BTC Articles #
## ### ## ### ##

btc = pd.read_csv("raw_data/bitcoin_news_articles.csv").sample(NUM_FILES_TO_SAMPLE * 4) # 3 # Get more than needed, since not all will work
btc["link"] = [article for article in get_text(btc["link"])]
btc = btc.dropna().sample(int(NUM_FILES_TO_SAMPLE * 0.75))
btc = dict(zip(["btc_" + str(id) for id in list(btc["article_id"])], list(btc["link"])))

data.update(btc)

### ## ### ## ###
# Instructables #
### ## ### ## ###

NUM_INSTRUCTABLE_CSVS = 6

def read_instructable_csv(path: str):
    '''
    Get Instrucable csv

    path: path to csv file

    returns: 
    '''
    return pd.read_csv(path).sample(
        NUM_FILES_TO_SAMPLE * 2 // NUM_INSTRUCTABLE_CSVS
    )  # We want an eequal number of each csv

diy = pd.concat(
    map(
        read_instructable_csv,
        [
            "raw_data/instructables/projects_circuits.csv",
            "raw_data/instructables/projects_cooking.csv",
            "raw_data/instructables/projects_craft.csv",
            "raw_data/instructables/projects_living.csv",
            "raw_data/instructables/projects_outside.csv",
            "raw_data/instructables/projects_workshop.csv",
        ],
    )
)

diy["Instructables-link"] = "https://www.instructables.com/" + diy["Instructables-link"]
diy["Instructables-link"] = list(get_text(diy["Instructables-link"])) # get text from urls
diy = dict(zip(["diy_" + str(id) for id in list(diy["Project-Title"])], list(diy["Instructables-link"])))

data.update(diy)

## ### ###
# README #
### ### ##

keys = []
for path, subdirs, files in os.walk("raw_data/readmes"):
    for name in files:
        key = os.path.join(path, name)
        keys.append(key)

readme = {}
for key in random.sample(keys, min(len(keys), int(NUM_FILES_TO_SAMPLE * 1.5))):
    with open(key, "r", encoding="latin1") as f:
        html = f.read()
        m = markdown(html)
        readme['readme_' + key.split('/')[-1][:-3]] = h.handle(html)

data.update(readme)

## ### #
# todo #
# ### ##

todo = pd.read_json("raw_data/todo.json")[["TaskTitle", "ListTitle"]]
# build todo lists from individual entries
todo = todo.groupby(["ListTitle"], as_index=False).agg({"TaskTitle": "\n".join})
todo["TaskTitle"] = todo["ListTitle"] + ":\n\n" + todo["TaskTitle"]
todo = dict(zip(["todo_" + str(id) for id in list(todo["ListTitle"])], list(todo["TaskTitle"])))

data.update(todo)

## ### ## #
# Journal #
# ### ## ##

jrnl = pd.read_csv("raw_data/journal_entries.csv")["Answer"].sample(NUM_FILES_TO_SAMPLE * 12)
jrnl = dict(zip(["jrnl_" + str(id) for id in list(jrnl.index)], list(jrnl)))

data.update(jrnl)

## ### ###
# Resume #
### ### ##

resume = pd.read_csv("raw_data/resumes.csv").sample(NUM_FILES_TO_SAMPLE * 2)
resume = dict(zip(["resume_" + str(id) for id in list(resume.index)], resume["Resume_html"].apply(h.handle)))

data.update(resume)

## ### ## ### ###
# Game Dialogue #
### ### ## ### ##

path = 'raw_data/game_dialogue/'
torchlight = pd.read_csv(path+'torchlight_ii.csv')[['raw_text']].sample(NUM_FILES_TO_SAMPLE * 3).rename(columns={"raw_text": "text"})
torchlight['id'] = 'game_torchlight-' + torchlight.index.astype(str)
starwars = pd.read_csv(path+'star_wars.csv')[['text']].sample(NUM_FILES_TO_SAMPLE * 3)
starwars['id'] = 'game_starwars-' + starwars.index.astype(str)
elderscrolls = pd.DataFrame(json.load(open(path+'elder_scrolls.json')).values())[['text']].sample(NUM_FILES_TO_SAMPLE * 3)
elderscrolls['id'] = 'game_elderscrolls-' + elderscrolls.index.astype(str)
game = pd.concat([torchlight, starwars, elderscrolls])
game = dict(zip(list(game['id']), list(game['text'])))

data.update(game)

## ### #
# Math #
# ### ##

keys = []
for path, subdirs, files in os.walk("raw_data/math"):
    for name in files:
        key = os.path.join(path, name)
        keys.append(key)

math = {}
for key in random.sample(keys, NUM_FILES_TO_SAMPLE * 12):
    with open(key, "r", encoding="latin1") as f:
        curr_json = json.load(f)
        curr_problem = curr_json["problem"] + ' \n ' +  curr_json["solution"]
        math['math_' + key.split('/')[-1][:-5]] = curr_problem

data.update(math)

## ### #
# Logs #
# ### ##

keys = []
for path, subdirs, files in os.walk("raw_data/logs"):
    for name in files:
        key = os.path.join(path, name)
        keys.append(key)

logs = {}
for key in keys:
    with open(key, "r", encoding="latin1") as f:
        lines = f.read().split('\n')
        lines = lines[:NUM_FILES_TO_SAMPLE * 8]
        logs['log_' + key.split('/')[-1][:-4]] = "\n".join(lines)

data.update(logs)

## ### ## ### ###
# Sanitize text #
### ### ## ### ##

def sanitize(text: str):
    '''
    Clean text for future processing

    text: string to be sanitized

    returns cleaned text
    '''
    # link = r"(https?:\/\/)?(www\.)?([\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+\.[\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+)+"
    # try:
    #     text = re.sub(link, " REPLACEDLINK ", text)
    # except:
    #     print(f"cannot replace link in:\t {text}")
    #text = re.sub(r"<.+?>", "", text) # remove HTML tages that werent caught
    text = re.sub(r"\u0000", "", text)
    text = re.sub(r"[\\/]", " ", text)
    text = re.sub(r"[^a-zA-Z\d\s@\.,!\?:;\']", "", text)
    text = re.sub(r"\s\s+", " ", text) # Normalize whitespaces to no more than once consecutively
    text = re.sub(r"\n\n+", "\n", text)
    text = re.sub(r"[^\s\.!:,\\/@;]{40,}", "", text)  # there are no words longer than 40 characters
    return text.strip()


data = {k: sanitize(v) for k, v in data.items() if v}

## ### ## ### ###
# Write to File #
### ### ## ### ##

with open("data/non_malicious_data.json", "w") as f:
    json.dump(data, f, ensure_ascii=False)
