import pandas as pd
import re

mal = pd.DataFrame(pd.read_json('data/malicious_data.json', typ='dictionary'))
mal[1] = 1
clean = pd.DataFrame(pd.read_json('data/non_malicious_data.json', typ='dictionary'))
clean[1] = 0

data = pd.concat([mal, clean]).reset_index()
data = data.rename(columns={"index": "id", 0: "text", 1: "label"})

data['type'] = data["id"].str.split('_').str[0]

def get_file_breakdown(df, breakdown_type: str):
    '''
    Get breakdown of amount of each data type
    '''
    num_files = len(df['label'])
    num_clean_files = sum(df['label']==0)
    num_mal_files = sum(df['label']==1)

    num_prose = sum(df['type'] == 'prose')
    num_em = sum(df['type'] == 'em')
    num_btc = sum(df['type'] == 'btc')
    num_diy = sum(df['type'] == 'diy')
    num_todo = sum(df['type'] == 'todo')
    num_jrnl = sum(df['type'] == 'jrnl')
    num_readme = sum(df['type'] == 'readme')
    num_resume = sum(df['type'] == 'resume')
    num_game = sum(df['type'] == 'game')
    num_math = sum(df['type'] == 'math')
    num_logs = sum(df['type'] == 'log')

    tot_clean = num_prose + num_em + num_btc +  num_diy + num_todo + num_jrnl + num_readme + num_resume + num_game + num_math + num_logs
    if num_clean_files != tot_clean:
        print(f'SANITY CHECK: {tot_clean} is NOT EQUAL to clean {num_clean_files}. Check code for errors.')

    print(f"Num of {breakdown_type} files: {num_files} \n\t{num_mal_files} malicous, {num_clean_files} clean \n\t{num_prose} prose, {num_em} email, {num_btc} btc articles, {num_diy} instruct, {num_todo} todo, {num_jrnl} journal, {num_readme} readme, {num_resume} resume, {num_game} game, {num_math} math, {num_logs} logs\n------")

    return(num_files, num_mal_files, num_clean_files, num_prose, num_em, num_btc, num_diy, num_todo, num_jrnl, num_readme, num_resume, num_game, num_math, num_logs)

print('=========\n  Total\n=========')
tot_breakdown = get_file_breakdown(data, "total")

# Split into sets
print('=========\n  Split\n=========')

train = data.groupby('type').sample(frac = 0.7)
evaluation = data.drop(train.index).groupby('type').sample(frac = 0.5)
test = data.drop(train.index).drop(evaluation.index)

train_breakdown = get_file_breakdown(train, "train")
eval_breakdown = get_file_breakdown(evaluation, "eval")
test_breakdown = get_file_breakdown(test, "test")

# Chunk into sequences of max 128 characters for model
print('===========\n  Chunked\n===========')

def chunks(lst, n): 
    return [' '.join(lst[x:x+n]) for x in range(0, len(lst), n)]

train['text'] = train['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()
evaluation['text'] = evaluation['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()
test['text'] = test['text'].apply(lambda txt: chunks(txt.split(' '), 128)).dropna()

train = train.explode('text')
train = train[train['text'].str.count(' ') > 10].reset_index() # At least 10 words
train['id'] += '_train' + train.index.astype(str)

evaluation = evaluation.explode('text')
evaluation = evaluation[evaluation['text'].str.count(' ') > 10].reset_index()
evaluation['id'] += '_valid' + evaluation.index.astype(str)

test = test.explode('text')
test = test[test['text'].str.count(' ') > 10].reset_index()
test['id'] += '_test' + test.index.astype(str)

train_breakdown = get_file_breakdown(train, "chunked train")
eval_breakdown = get_file_breakdown(evaluation, "chunked eval")
test_breakdown = get_file_breakdown(test, "chunked test")

print('==========\n  Capped\n==========')

# ensure all data types have the same amount of chunks (capped to ransom chunk amount) if possible
train = train.groupby('type').apply(lambda x: x.sample(n=min(len(x), train_breakdown[1])))
evaluation = evaluation.groupby('type').apply(lambda x: x.sample(n=min(len(x), eval_breakdown[1])))
test = test.groupby('type').apply(lambda x: x.sample(n=min(len(x), test_breakdown[1])))

train_breakdown = get_file_breakdown(train, "chunked + capped train")
eval_breakdown = get_file_breakdown(evaluation, "chunked + capped eval")
test_breakdown = get_file_breakdown(test, "chunked + capped test")

train.to_csv('data/train.csv', index = False, columns = ['id', 'text', 'label'])
evaluation.to_csv('data/eval.csv', index = False, columns = ['id', 'text', 'label'])
test.to_csv('data/test.csv', index = False, columns = ['id', 'text', 'label'])
