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

def patt():
    #wh-word(+ whether + if) + NP + VP
    start = '<consider\sVVI><that\s[A-Z]+>'
    #wh-words + whether&if
    noun_phrase = nounp()
    verb = '(?:<[^>]+?\sV..>)'

    pattern = start + noun_phrase

    return pattern


def search(pattern, directory):
    errors = []
    folders = os.listdir(directory)
    b = 0
    print(folders)
    for folder in folders:
        print(folder)
        if folder == '.DS_Store':
            continue
        files = os.listdir(directory + folder)
        print(len(files))
        for file in files:

            if file == '.DS_Store':
                continue
            text = open_file(directory + folder + '/' + file)
            sentences = text.split('@')
            for sent in sentences:
                if re.search(pattern, sent, flags=re.IGNORECASE):
                    if (re.sub('' + pattern, '', sent)) == '<. SENT>':
                        continue
                    errors.append([re.sub('^\n', '', sent), file, folder])
                    print(sent)

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
    pattern = patt()
    errors = search(pattern, directory='tags/')
    filename = 'consider.xls'

    writeln(errors, filename)
    nounp()

if __name__ == '__main__':
    main()