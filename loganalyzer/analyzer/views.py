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
    client_number = 0
    connection_number = 0
    active_session = False
    path = False
    path_part = 0
    client_name = ''
    client_path = 0

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
            elif length == 4:
                if re.match('^VCS Provider: .+$',line.strip()):
                    splitted = line.split(':')
                    structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]].update(OrderedDict({'VCS Provider': str(splitted[1]).strip()}))
                elif subsections[3] == 'Team Settings':
                    splitted = line.split(':')
                    if str(splitted[0]).strip() == 'Integrate with Version Control':
                        structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]].update(OrderedDict({str(splitted[0]).strip(): OrderedDict()}))
                    else:
                        structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]].update(OrderedDict({ str(splitted[0]).strip() : str(splitted[1]).strip()}))
                else:
                    structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]].update(OrderedDict({str(text[3]).strip(): OrderedDict()}))
                    if len(subsections) > 4:
                        subsections[4] = str(text[3]).strip()
                    else:
                        subsections.append(str(text[3]).strip())
            elif length == 5:
                if re.match('^VCS Project: .+$',line.strip()):
                    splitted = line.split(':')
                    structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]].update(OrderedDict({'VCS Project': OrderedDict({'Name': str(splitted[1]).strip()}) }))
                    if len(subsections) > 5:
                        subsections[5] = 'VCS Project'
                    else:
                        subsections.append('VCS Project')
                    continue
                elif re.match('^VCS Provider: .+$',line.strip()):
                    splitted = line.split(':')
                    #structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]].update(OrderedDict({str(splitted[0]).strip(): str(splitted[1]).strip()  }))
                else:
                    structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]].update(OrderedDict({str(text[4]).strip(): OrderedDict()}))

                    if len(subsections) > 5:
                        subsections[5] = str(text[4]).strip()
                    else:
                        subsections.append(str(text[4]).strip())
            elif length == 6:
                splitted = line.split(':')
                structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]][subsections[5]].update(OrderedDict({str(splitted[0]).strip(): OrderedDict()}))
                if len(subsections) > 6:
                    subsections[6] = str(splitted[0]).strip()
                else:
                    subsections.append(str(splitted[0]).strip())
            elif length ==7:
                splitted = line.split(':')
                structure[subsections[0]][subsections[1]][subsections[2]][subsections[3]][subsections[4]][subsections[5]][subsections[6]].update(OrderedDict({str(splitted[0]).strip(): str(splitted[1]).strip() }))
        elif subsections[0]=='MANAGED ITEMS':
            structure[subsections[0]].update(OrderedDict({'Value': line}))
        elif subsections[0]=='ORACLE CLIENT INFORMATION':
            splitted = line.split(':')
            if splitted[0].strip() == 'Oracle Client Version':
                client_number = client_number + 1
                structure[subsections[0]].update(OrderedDict({'Oracle Client ('+ str(client_number) +')': OrderedDict()}))
            structure[subsections[0]]['Oracle Client ('+ str(client_number) +')'].update(OrderedDict({str(splitted[0]): ':'.join(splitted[1:]).strip()}))
        elif subsections[0]=='ORACLE SERVER INFORMATION':
            splitted = line.split(':')
            if re.match('^Connection [0-9]+$',splitted[0].strip()):
                connection_number = connection_number + 1
                structure[subsections[0]].update(OrderedDict({'Connection ('+ str(connection_number) +')': OrderedDict()}))
                if re.match('.+ Active Session .+', line):
                    active_session = True
                else:
                    active_session = False
                structure[subsections[0]]['Connection (' + str(connection_number) + ')'].update(OrderedDict({'Active Session': str(active_session)}))
            structure[subsections[0]]['Connection (' + str(connection_number) + ')'].update(OrderedDict({str(splitted[0]): str(':'.join(splitted[1:]).split('**')[0]).strip()}))
        elif subsections[0]=='SYSTEM INFORMATION':
            splitted = line.split(':')
            if splitted[0].strip() == 'Environment Variable (PATH)':
                path = True
                structure[subsections[0]].update(OrderedDict({'Environment Variable (PATH)': OrderedDict()}))
            elif splitted[0].strip() == 'Environment Variable (TNS_ADMIN)':
                path = False
            if path:
                structure[subsections[0]]['Environment Variable (PATH)'].update(OrderedDict({path_part: ':'.join(splitted).strip()}))
                path_part = path_part + 1
            else:
                structure[subsections[0]].update(OrderedDict({str(splitted[0]): str(':'.join(splitted[1:])).strip()}))
        elif subsections[0] == 'ORACLE HOMES DATA':
            splitted = line.split('=')
            if line.strip() == '(Oracle Root)':
                structure[subsections[0]].update(OrderedDict({ '(Oracle Root)' : OrderedDict()}))
            elif splitted[0].strip() == 'inst_loc':
                structure[subsections[0]]['(Oracle Root)'].update(OrderedDict({'inst_loc': splitted[1].strip()}))
            elif len(line.split('-')) == 2:
                splitted = line.split('-')
                client_path = 0
                if len(subsections) > 1:
                    if subsections[1] == str(splitted[0].strip()).strip():
                        continue
                    subsections[1] = str(splitted[0].strip()).strip()
                else:
                    subsections.append(str(splitted[0].strip()).strip())
                    structure[subsections[0]].update(OrderedDict({str(splitted[0].strip()).strip(): OrderedDict({'version': str(splitted[1].strip()).strip()})}))
            elif len(splitted) == 2:
                structure[subsections[0]][subsections[1]].update(OrderedDict({str(splitted[0]).strip() : str(splitted[1]).strip()}))
            else:
                structure[subsections[0]][subsections[1]].update(OrderedDict({str(client_path): line.strip()}))
                client_path = client_path + 1
        elif subsections[0] == 'FORMATTER OPTIONS':
            if line =='[Qp5FormatterOptions]':
                structure[subsections[0]].update(OrderedDict({'Qp5FormatterOptions': OrderedDict()}))
                if len(subsections) > 1:
                    subsections[1] = 'Qp5FormatterOptions'
                else:
                    subsections.append('Qp5FormatterOptions')
            else:
                splitted = line.split('=')
                structure[subsections[0]][subsections[1]].update(OrderedDict({str(splitted[0].strip()): splitted[1].strip()}))
                #structure[subsections[0]][subsections[1]].update(OrderedDict({str(splitted[0]).strip(): str(splitted[1]).strip()}))

    pprint(structure['ORACLE HOMES DATA'])

