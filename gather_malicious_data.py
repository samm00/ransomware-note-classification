import os
import json
import re
import string
import html2text

data = {}
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True

for path, subdirs, files in os.walk('raw_data/ransom_notes/'):
    for name in files:
        key = os.path.join(path, name)
        try:
            with open(key, 'r') as f:
                text = f.read()
                if name == '!Recovery_[].html':
                    text = re.sub(r'<span class=\'v9OFef\'>.*?</span>', '', text)
                if 'Locky' in key:
                    for clas in ['jrbjqugvlw', 'iussrkmwvnx', 'zjewa', 'koeyrzco', 'rkika', 'rlrclkc', 'tzhudfuleftto', 'uljhfiqsmz', 'zzhkar', 'odysnn']:
                        text = re.sub(r'<span class=\'' + clas + r'\'>.*?</span>', ' ', text)
                    for clas in ['zudrfc', 'hcwepklpwx', 'rtlxkvpg', 'crqtblq', 'rsotyqx', 'kweopqwzud', 'nzxohe', 'zqlvgwing']:
                        text = re.sub(r'<div class=' + clas + r'>.*?</div>', ' ', text)
                if 'Cerber' in key:
                    text = re.sub(r'<span class=\"h\">.*?<\/span>', '', text)
                    text = text[text.index('HERE1')+5:text.index('لا')]
                if 'Matrix' in key:
                    for code in [r'\\lang1049', r'\\lang1033', r'\\par', r'\\f0 ', r'\\f0', r'\\f1 ', r'\\f1', r'\\fs28', r'\\fs32', r'\\b0', r'\\b', r'\\fs24', r'\\cf1', r'\\cf00', r'd\\ri-74', r'd?\\sa200\\sl240\\slmult1', r'\\tx8378 ', r'.*\n.*\n.*\\tx8804']:
                        text = re.sub(code, '', text)
                    text = re.sub(r'\\\'ee', 'o', text)
                    text = re.sub(r'\\\'e0', 'a', text)
                    text = re.sub(r'\\\'c0', 'a', text)
                    text = re.sub(r'\\\'e5', 'e', text)
                    text = re.sub(r'\\\'c5', 'e', text)
                    text = re.sub(r'\\\'f0', 'p', text)
                    text = re.sub(r'\\\'f1', 'c', text)
                    text = re.sub(r'\\\'f3', 'y', text)
                if name[-4:] == 'html' or name[-3:] == 'hta' or name[-3:] == 'htm':
                    text = h.handle(text)
                if name == '!HELP_SOS.hta':
                    text = text[text.index('HERE1')+5:text.index('HERE2')]

                #link = r'(https?:\/\/)?(www\.)?([\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+\.[\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+)+'
                #text = re.sub(link, ' REPLACEDLINK ', text)
                #text = re.sub(r'<.+?>', '', text)
                text = re.sub(r'\u0000', '', text)
                text = re.sub(r'[\\/]', ' ', text)
                text = re.sub(r'[^a-zA-Z\d\s@\.,!\?:;\']', '', text)
                text = re.sub(r'\s\s+', ' ', text)
                text = re.sub(r'[^\s\.!:,\\/@;]{20,}', '', text)
                data['ransom_' + key[16:]] = text.strip()
        except:
            with open(key, 'r', encoding = 'latin-1') as f:
                text = f.read()
                if name[-4:] == 'html' or name[-3:] == 'hta' or name[-3:] == 'htm':
                    text = h.handle(text)
                # link = r'(https?:\/\/)?(www\.)?([\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+\.[\[\]_\.~!\*\'();:@&=\+\$,\/\?%#A-z0-9]+)+'
                # text = re.sub(link, ' REPLACEDLINK ', text)
                # text = re.sub(r'<.+?>', '', text) # remove HTML tages that werent caught
                text = re.sub(r'\u0000', '', text)
                text = re.sub(r'[\\/]', ' ', text)
                text = re.sub(r'[^a-zA-Z\d\s@\.,!\?:;\']', '', text)
                text = re.sub(r'\s\s+', ' ', text)
                text = re.sub(r'[^\s\.!:,\\/@;]{40,}', '', text)
                data['ransom_' + key[16:]] = text.strip()

with open('data/malicious_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii = False)