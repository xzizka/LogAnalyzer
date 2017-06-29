from . import analyzer
import json, re
from collections import OrderedDict
from pprint import pprint
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

    process_SB(files['sb.txt'])

    return files


def process_SB(file):
    structure = OrderedDict()
    subsections = []
    splitted = []
    for line in file.splitlines():
        if re.match(r'[\*]+$',line) or re.match(r'\ufeff[\*]+$',line) or re.match(r'^$',line):
            continue # removes lines full of stars (delimiters) and empty lines
        elif re.match(r'^\*\*\s.+$', line):
            subsections = []
            if re.match(r'^\*\* FORMATTER OPTIONS:(.|\s)+', line):
                structure.update({ 'FORMATTER OPTIONS': { 'Path': ''.join(line.split(':')[1:]).strip() } })
                if len(subsections) >= 1:
                    subsections[0] = 'FORMATTER OPTIONS'
                else:
                    subsections.append('FORMATTER OPTIONS')
            elif re.match('^\*\* APPLICATION INFORMATION - .+$',line):
                structure.update(OrderedDict({ 'APPLICATION INFORMATION': OrderedDict( { 'Version': str('-'.join(line.split('-')[1:])).strip() }) }))
                if len(subsections) >= 1:
                    subsections[0] = 'APPLICATION INFORMATION'
                else:
                    subsections.append('APPLICATION INFORMATION')
            else:
                if len(subsections) >= 1:
                    subsections[0] = line[2:].strip()
                else:
                    subsections.append(line[2:].strip())
                structure.update({ line[2:].strip(): OrderedDict() })
            continue
        elif subsections[0] == 'APPLICATION INFORMATION':
            splitted = []
            if re.match(r'^Support Bundle for Toad for Oracle .+$',line):
                structure[subsections[0]].update({ 'Toad for Oracle version':  re.compile(r'\d+.\d+.\d+.\d+$').search(line).group().strip() } )
            elif re.match('^This copy of Toad for Oracle registered to .+$',line):
                structure[subsections[0]].update({ 'Registration':  str(line[42:]).strip() } )
            elif re.match('^Bundle: .+$',line):
                splitted = line.split(',')
                structure[subsections[0]].update({'Bundle': str(''.join(splitted[0].split(':')[1:])).strip() })
                structure[subsections[0]].update({'Add-Ons': str(''.join(splitted[1].split(':')[1:])).strip() })
            elif re.match('^Edition: .+$',line):
                structure[subsections[0]].update({'Edition': str(''.join(line.split(':')[1:])).strip() })
            else:
                splitted = line.split(':')
                structure[subsections[0]].update({ splitted[0].strip() : str(':'.join(splitted[1:])).strip() })
            continue
        elif subsections[0] == 'TEAM CODING':
            text = line.split('\t')
            length = len(text)
            #pprint(text)
            if length == 1:
                splitted = line.split(':')
                structure[subsections[0]].update(OrderedDict({ str(':'.join(splitted[1:])).strip() : OrderedDict() }))
                if len(subsections) >2 :
                    subsections[1] = str(':'.join(splitted[1:])).strip()
                else:
                    subsections.append(str(':'.join(splitted[1:])).strip())
            elif length == 2:
                if re.match('Team Coding@.+$',str(text[1]).strip()):
                    item = OrderedDict()
                else:
                    item = []
                structure[subsections[0]][subsections[1]].update(OrderedDict({str(text[1]).strip(): item }))
                if len(subsections) >2 :
                    subsections[2] = str(text[1]).strip()
                else:
                    subsections.append(str(text[1]).strip())
            elif length == 3:
                #pprint(subsections)
                #print('------------')
                #pprint(text[2])
                if re.match('Team Coding@.+$',subsections[2]):
                    structure[subsections[0]][subsections[1]][subsections[2]].update(OrderedDict({ str(text[2]).strip() : OrderedDict() }))
                else:
                   structure[subsections[0]][subsections[1]][subsections[2]].append( str(text[2]).strip() )
                   if len(subsections) > 3:
                       subsections[3] = str(text[2]).strip()
                   else:
                       subsections.append(str(text[2]).strip())

    pprint(json.dumps(structure))

    '''
    This procedure parses the TFO SB
    
    structure = {} # structure with reworked data
    next_step = 0 # variable used for forwarding in the process tree
    level = 0 # level in structure
    previous_level= 0 # previous level in the structure
    subsections = []
    for line in file.splitlines():
        if re.match(r'[\*]+$',line) or re.match(r'\ufeff[\*]+$',line) or re.match(r'^$',line):
            continue # removes lines full of stars (delimiters) and empty lines
        elif re.match(r'^\*\*\s.+$',line):
            subsections = []
            if re.match(r'^\*\* FORMATTER OPTIONS:(.|\s)+',line):
                structure['FORMATTER OPTIONS'] = {}
                structure['FORMATTER OPTIONS']['Path'] = ''.join(line.split(':')[1:]).strip()
                subsections.append("FORMATTER OPTIONS")
            else:
                subsections.append(line[2:].strip())
                structure[subsections[0]] = {}
            next_step = 0
            continue
        elif re.match(r'^Support Bundle for Toad for Oracle .+$',line):
            structure[subsections[0]]['Toad for Oracle version'] =  re.compile(r'\d+.\d+.\d+.\d+$').search(line).group().strip()
            next_step = 1
            continue
        elif next_step == 1:
            structure[subsections[0]]['Comment'] = line
            next_step = 2
            continue
        elif next_step == 2:
            splitted = line.split(':')
            structure[subsections[0]][splitted[0].strip()] = splitted[1].split(',')[0].strip()
            structure[subsections[0]][splitted[1].split(',')[1].strip()] = splitted[2].strip()
            next_step=3
            continue
        elif next_step == 3:
            splitted = line.split(':')
            structure[subsections[0]][splitted[0].strip()] = ''.join(splitted[1:])
            continue
        elif subsections[0] == "TEAM CODING":
            text = line.split('\t')
            length = len(text)
            if next_step == 0 and re.match(r'^Connection: .+$', line):
                splitted = line.split(' ')
                structure[subsections[0]]['string'] = splitted[1].strip()
                next_step = 4
                level = 1
                continue
            elif next_step == 4:
                temp = structure
                i = 0
                while i < level:
                    i = i + 1
                    temp = temp[subsection[i]]

                if level > previous_level:
                    pass
                    previous_level = level
                elif level == previous_level:
                    previous_level = level
                else:
                    temp.update({ : })
                    previous_level = level
                    pass
                if re.match(r'\t\t\t\t\t\t.+$', line):
                    #structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]][subsections[5]] = line.strip()
                    continue
                elif re.match(r'\t\t\t\t\t.+$', line):
                    #subsections[5] = line.strip()
                    #structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]] = { line.strip(): {} }
                    continue

    pprint(structure['TEAM CODING'])
    '''