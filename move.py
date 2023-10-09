import os

for path, subdirs, files in os.walk('ransom_notes'):
    for name in files:
        key = os.path.join(path, name)
        new_path = '_'.join(key.split('/')[1:])
        os.popen(f'cp \"{key}\" \"data/{new_path}\"')