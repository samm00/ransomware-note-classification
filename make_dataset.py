import pandas as pd
import re

mal = pd.DataFrame(pd.read_json('malicious_data.json', typ='dictionary'))
mal[1] = 1
clean = pd.DataFrame(pd.read_json('clean_data.json', typ='dictionary'))
clean[1] = 0

data = pd.concat([mal, clean]).reset_index()
data = data.rename(columns={"index": "id", 0: "text", 1: "label"})

print(len(data['label']))

train = data.sample(frac = 0.7)
evaluation = data.drop(train.index).sample(frac = 0.5)
test = data.drop(train.index).drop(evaluation.index)

print(len(train['label']))
print(len(evaluation['label']))
print(len(test['label']))

def chunks(lst, n): 
    return [' '.join(lst[x:x+n]) for x in range(0, len(lst), n)]
train['text'] = train['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()
evaluation['text'] = evaluation['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()
test['text'] = test['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()

train = train.explode('text')
train = train[train['text'].str.count(' ') > 13].reset_index()
train['id'] += '_train' + train.index.astype(str)

evaluation = evaluation.explode('text')
evaluation = evaluation[evaluation['text'].str.count(' ') > 13].reset_index()
evaluation['id'] += '_valid' + evaluation.index.astype(str)

test = test.explode('text')
test = test[test['text'].str.count(' ') > 13].reset_index()
test['id'] += '_test' + test.index.astype(str)

print(len(train['label']))
print(len(evaluation['label']))
print(len(test['label']))

train.to_csv('train.csv', index = False, columns = ['id', 'text', 'label'])
evaluation.to_csv('eval.csv', index = False, columns = ['id', 'text', 'label'])
test.to_csv('test.csv', index = False, columns = ['id', 'text', 'label'])
