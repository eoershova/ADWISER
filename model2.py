import re
import os
import csv


# gets all the essays from a particular folder
def file_finder():
    where = 'ttags/'
    file_address = 'ttags/'
    files = os.listdir(file_address)
    txt_files = []
    for i in files:
        if i.endswith('.txt'):
            txt_files.append(i)
    # print(files)
    return file_address, txt_files, where


# looks for a pattern specified in the reg ex
def search(txt_files, where):
    file_address = 'ttags/'
    for essay in txt_files:
        essay_address = file_address + '/' + essay
        with open(essay_address, 'r', encoding='utf-8') as file:
            text = file.read()
            sentences = text.split('@')
            for sentence in sentences:
                sentence = re.sub('<[,;:%()-]\sPUNCT>', '', sentence) # because we don't account for it in this model
                sentence = re.sub('<\s\sSPACE>', '', sentence) # because of the annotation format
                perfect_context = re.compile("<((have|has|'ve)\sVERB><[a-zA-z]+\sVERB)")
                perfect_contexts = re.findall(perfect_context, sentence)
                if len(perfect_contexts) != 0:
                    print(sentence)
                    trigger_1 = re.compile("<in\sADP><[a-zA-z]+\s[A-Z]+><[a-zA-z\d]+\sNUM>")
                    trigger_2 = re.compile("<in\sADP><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z\d]+\sNUM>")
                    trigger_3 = re.compile(
                        "<in\sADP><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z\d]+\sNUM>")
                    trigger_4 = re.compile(
                        "<in\sADP><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z\d]+\sNUM>")
                    trigger_5 = re.compile(
                        "<in\sADP><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z]+\s[A-Z]+><[a-zA-z\d]+\sNUM>")
                    triggers = [ trigger_1, trigger_2, trigger_3, trigger_4, trigger_5]
                    n = -1
                    for trigger in triggers:
                        n += 1
                        triggered = re.findall(trigger, sentence)
                        if len(triggered) != 0:
                            csv_table_writer(sentence, n)
                            print(sentence)
                            break


# writes the sentence and the amount of words that are between IN and NUM
def csv_table_writer(sentence, n):
    sentence = sentence.split('<')[0]
    words = n
    with open('tablet.csv', mode='a+', encoding="utf-8") as csv_file:
        fieldnames = ['sentence', 'words between']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writerow({'sentence': sentence, 'words between': words})


def main():
    file_address, txt_files, where = file_finder()
    search(txt_files, where)


if __name__ == '__main__':
    main()