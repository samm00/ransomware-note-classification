import pandas as pd
import re

mal = pd.DataFrame(pd.read_json('data/malicious_data.json', typ='dictionary'))
mal[1] = 1
clean = pd.DataFrame(pd.read_json('data/non_malicious_data.json', typ='dictionary'))
clean[1] = 0

data = pd.concat([mal, clean]).reset_index()
data = data.rename(columns={"index": "id", 0: "text", 1: "label"})

def get_file_breakdown(df):
    num_files = len(df['label'])
    num_clean_files = sum(df['label']==0)
    num_mal_files = num_files - num_clean_files

    num_prose = sum(df['id'].str.contains('prose'))
    num_em = sum(df['id'].str[:2] == 'em')
    num_btc = sum(df['id'].str[:3] == 'btc')
    num_diy = sum(df['id'].str[:3] == 'diy')
    num_todo = sum(df['id'].str[:4] == 'todo')
    num_jrnl = sum(df['id'].str[:4] == 'jrnl')
    num_readme = sum(df['id'].str.contains('READMEs_en'))

    tot_clean = num_prose + num_em + num_btc +  num_diy + num_todo + num_jrnl + num_readme
    if num_clean_files != tot_clean:
        print(f'{tot_clean} is NOT EQUAL to clean')

    return(num_files, num_mal_files, num_clean_files, num_prose, num_em, num_btc, num_diy, num_todo, num_jrnl, num_readme)

tot_breakdown = get_file_breakdown(data)
print(f"Num of files: {tot_breakdown[0]} \n\t{tot_breakdown[1]} malicous, {tot_breakdown[2]} clean \n\t{tot_breakdown[3]} prose, {tot_breakdown[4]} email, {tot_breakdown[5]} btc articles, {tot_breakdown[6]} instruct, {tot_breakdown[7]} todo, {tot_breakdown[8]} journal, {tot_breakdown[9]} readme\n------")

train = data.sample(frac = 0.7)
evaluation = data.drop(train.index).sample(frac = 0.5)
test = data.drop(train.index).drop(evaluation.index)

train_breakdown = get_file_breakdown(train)
eval_breakdown = get_file_breakdown(evaluation)
test_breakdown = get_file_breakdown(test)
print(f"Num of train files: {train_breakdown[0]} \n\t{train_breakdown[1]} malicous, {train_breakdown[2]} clean \n\t{train_breakdown[3]} prose, {train_breakdown[4]} email, {train_breakdown[5]} btc articles, {train_breakdown[6]} instruct, {train_breakdown[7]} todo, {train_breakdown[8]} journal, {train_breakdown[9]} readme")
print(f"Num of eval files: {eval_breakdown[0]} \n\t{eval_breakdown[1]} malicous, {eval_breakdown[2]} clean \n\t{eval_breakdown[3]} prose, {eval_breakdown[4]} email, {eval_breakdown[5]} btc articles, {eval_breakdown[6]} instruct, {eval_breakdown[7]} todo, {eval_breakdown[8]} journal, {eval_breakdown[9]} readme")
print(f"Num of test files: {test_breakdown[0]} \n\t{test_breakdown[1]} malicous, {test_breakdown[2]} clean \n\t{test_breakdown[3]} prose, {test_breakdown[4]} email, {test_breakdown[5]} btc articles, {test_breakdown[6]} instruct, {test_breakdown[7]} todo, {test_breakdown[8]} journal, {test_breakdown[9]} readme\n------")

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

train_breakdown = get_file_breakdown(train)
eval_breakdown = get_file_breakdown(evaluation)
test_breakdown = get_file_breakdown(test)
print(f"Num of train chunks: {train_breakdown[0]} \n\t{train_breakdown[1]} malicous, {train_breakdown[2]} clean \n\t{train_breakdown[3]} prose, {train_breakdown[4]} email, {train_breakdown[5]} btc articles, {train_breakdown[6]} instruct, {train_breakdown[7]} todo, {train_breakdown[8]} journal, {train_breakdown[9]} readme")
print(f"Num of eval chunks: {eval_breakdown[0]} \n\t{eval_breakdown[1]} malicous, {eval_breakdown[2]} clean \n\t{eval_breakdown[3]} prose, {eval_breakdown[4]} email, {eval_breakdown[5]} btc articles, {eval_breakdown[6]} instruct, {eval_breakdown[7]} todo, {eval_breakdown[8]} journal, {eval_breakdown[9]} readme")
print(f"Num of test chunks: {test_breakdown[0]} \n\t{test_breakdown[1]} malicous, {test_breakdown[2]} clean \n\t{test_breakdown[3]} prose, {test_breakdown[4]} email, {test_breakdown[5]} btc articles, {test_breakdown[6]} instruct, {test_breakdown[7]} todo, {test_breakdown[8]} journal, {test_breakdown[9]} readme")

train.to_csv('data/train.csv', index = False, columns = ['id', 'text', 'label'])
evaluation.to_csv('data/eval.csv', index = False, columns = ['id', 'text', 'label'])
test.to_csv('data/test.csv', index = False, columns = ['id', 'text', 'label'])
