from . import analyzer
from zipfile import ZipFile

def oracleSB(file):
    files = {}
    with ZipFile(file, 'r') as zipfile:
        for filename in zipfile.namelist():
            #files.append(zipfile.read(filename))
            #zipfile.extract(filename,'/tmp/extract/')
            with zipfile.open(filename) as innerfile:
                if filename == "Toad.el":
                    files[filename] = str(innerfile.read(),'utf-16')
                else:
                    files[filename] = str(innerfile.read(), 'utf-8')

    return files