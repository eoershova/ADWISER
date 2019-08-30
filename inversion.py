import re, os, pprint, xlsxwriter

def open_file(filename):
    with open(filename, encoding='utf-8') as f:
        text = f.read()
    return text

def nounp():
    base = '(?:(?:(?:<[^>]+?\sAV0>)?(?:<[^>]+?\s(?:[DA][TP].|POS)>)?(?:<[^>]+?\sAV0>)?' +\
           '(?:<[^>]+?\s[DA]T.>)?(?:<[^>]+?\s.RD>)?(?:<[^>]+?\sAJ.>)?)*'
    #facultative attributes of NOUN
    dnoun = '(?:<[^>]+?\sN..>' + base + '<[^>]+?\sN..>))'
    # such as "college student"
    noun_phrase1 = base + '(?:<[^>]+?\s(?:N..|PN.)>))'
    #such as "actually the best extremely poor student"
    noun_phrase2 = base + dnoun + ')'
    #base and "college student"
    noun_phrase3 = base + '(?:' + dnoun + '|' + '(?:<[^>]+?\s(?:N..|PN.)>))' + '<[^>]+\sPRF>' +\
                   '(?:' + dnoun + '|' + '(?:<[^>]+?\s(?:N..|PN.)>)))'
    #constructions with "of" such as "a perfect piece of cake"
    noun_phrase10 = '(?:<[^>]+?>){0,4}(?:<[^>]+?\s(?:N..|PN.)>)'
    noun_phrase =  '(?:' + noun_phrase2 + '|' + noun_phrase1 + '|' + noun_phrase3 + ')'
    #print(noun_phrase)
    return noun_phrase


def verbp():
    '''неготовая VP'''
    verb = '(?:<[^>]+?\sV..>)'
    to = '(?:<to\sPRP>' + nounp() + ')'
    verb_phrase = verb + to
    
    return verb_phrase

def patt():
    #context Verb/aux + ,(?) + wh-word(+ whether + if) + aux + NP + VP
    start = '(?:<[^>]+?\sV..>)(?:,\sPUN)?(?:<[^>]+?\s(?:AVQ|PNQ|DTQ)>|<[whether|if]\s.+?>)(?:<[^>]+?\sV[B|D|H|M].>)'
    #1: all verbs, 2: comma, 3: wh-words + whether&if, 4: auxiliaries (be, do, have, modal)
    noun_phrase = nounp()
    verb = '(?:<[^>]+?\sV..>)'
    pattern = start + noun_phrase + verb
    return pattern

def search(pattern, directory='tags/'):
    errors = []
    folders = os.listdir(directory)
    for folder in folders:
        print(folder)
        if folder != '.DS_Store':
            folder_address = directory + folder
            files = os.listdir(folder_address)
            for file in files:
                if file != '.DS_Store':
                    text = open_file(folder_address + '/' + file)
                    sentences = text.split('@')
                    for sent in sentences:
                        if '?' not in sent: ##looking for sentences without '?'
                            if re.search(pattern, sent, flags=re.IGNORECASE):
                                errors.append([re.sub('^\n', '', sent), file, directory])
    return errors

def writeln(errors, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    for error in errors:
        worksheet.write(row, col, error[0])
        worksheet.write(row, col + 1, error[1])
        worksheet.write(row, col + 2, error[2])
        row += 1
    workbook.close()

def main():
    a = search(patt())
    writeln(a, 'new_inversion.xlsx')
    #pprint.pprint(a)
    #print(len(a))

if __name__ == '__main__':
    main()
