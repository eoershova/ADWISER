import re
import treetaggerwrapper
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR='tt/')

# using a random text from corpus as user_input
def text_finder():

    with open('perf.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def preprocessing(user_input):
    data = []
    # prepare text for splitting into sentences
    user_input = re.sub(r'\n', ' ', user_input)
    user_input = re.sub(r'\s\s', ' ', user_input)
    user_input = re.sub(r'\.\s', '.\n', user_input)
    user_input = re.sub(r'\?\s', '?\n', user_input)
    user_input = re.sub(r'!\s', '!\n', user_input)
    sentences = user_input.split('\n')
    # tagging sentences
    for sentence in sentences:
        sentence_data = []
        if sentence != '':
            sentence_data.append(sentence)
            tags = tagger.tag_text(sentence)
            sp = []
            for tag in tags:
                word, tag, lemma = tag.split('\t')
                nl = '<' + word + ' ' + tag + '>'
                sp.append(nl)
            spstr = ''.join(sp)
            sentence_data.append(spstr)
        data.append(sentence_data)
    return data


def main():
    user_input = text_finder()
    data = preprocessing(user_input)




if __name__ == '__main__':
    main()
