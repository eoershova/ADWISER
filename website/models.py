# coding=utf-8
import re
import treetaggerwrapper

def models(user_input):
    tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR='tt/')

    def preprocessing(text):
        user_input = text
        data = []
        # prepare text for splitting into sentences
        user_input = re.sub(r'\n', ' ', user_input)
        user_input = re.sub(r'\s\s', ' ', user_input)
        user_input = re.sub(r'\s\:', ':', user_input)
        user_input = re.sub(r'\s\;', ';', user_input)
        user_input = re.sub(r'\s\,', ',', user_input)
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
        clean_data = []
        for sentence in data:
            if sentence != []:
                clean_data.append(sentence)
        data = clean_data
        print(data)
        # sent[0] - plaintext sentence, sent[1] - tagged sentence
        return data

    def open_file(filename):
        with open(filename, encoding='utf-8') as f:
            text = f.read()
        return text

    def nounp():
        base = '(?:(?:(?:<[^>]+?\sAV0>)?(?:<[^>]+?\s(?:[DA][TP].|POS)>)?(?:<[^>]+?\sAV0>)?' + \
               '(?:<[^>]+?\s[DA]T.>)?(?:<[^>]+?\s.RD>)?(?:<[^>]+?\sAJ.>)?)*'
        # facultative attributes of NOUN
        dnoun = '(?:<[^>]+?\sN..>' + base + '<[^>]+?\sN..>))'
        # such as "college student"
        noun_phrase1 = base + '(?:<[^>]+?\s(?:N..|PN.)>))'
        # such as "actually the best extremely poor student"
        noun_phrase2 = base + dnoun + ')'
        # base and "college student"
        noun_phrase3 = base + '(?:' + dnoun + '|' + '(?:<[^>]+?\s(?:N..|PN.)>))' + '<[^>]+\sPRF>' + \
                       '(?:' + dnoun + '|' + '(?:<[^>]+?\s(?:N..|PN.)>)))'
        # constructions with "of" such as "a perfect piece of cake"
        noun_phrase10 = '(?:<[^>]+?>){0,4}(?:<[^>]+?\s(?:N..|PN.)>)'
        noun_phrase = '(?:' + noun_phrase2 + '|' + noun_phrase1 + '|' + noun_phrase3 + ')'
        # print(noun_phrase)
        return noun_phrase

    def pp_time(data):
        have_forms = r"<(have|has)\sV[A-Z]+>"
        verb_3_form = r"<([a-z]+)\sVVN|VBN>"
        word = "(?:<([a-z']+)\s[A-Z\d]+>){0,4}"
        perfect = have_forms + word + verb_3_form

        # triggers as described in doc
        trigger1 = r'((In|in)\s(the\syear\s)?\d{4})'
        trigger2 = r'((Between|between)\s(the\syears\s)?(the\syear\s)?(years\s)?\d{4}\s)'
        trigger3 = r'((From|from)\s(the\s)?(year\s)?(years\s)?\d{4})'
        trigger4_1 = r'((at|in|during|At|In|During)\s(the\s)?(first|second|third|fourth|fifth|initial|last))\s'
        trigger4_2 = r'((stage|point|phase|period|year|decade|century))'
        trigger4 = trigger4_1 + trigger4_2
        trigger5 = r'((long)?\sago\s)'
        trigger6 = r'((Last|last)\s(year|term|summer|century))'
        trigger7 = r'((Since|since)\s\d{4}\sto\s\d{4})'
        trigger8 = r'((Over|over)\s\d+years)'
        triggers = [trigger1, trigger2, trigger3, trigger4, trigger5, trigger6, trigger7, trigger8]
        for sent in data:
            print(sent)
            if sent != []:
                # pp + time
                if re.search(perfect, sent[1], flags=re.IGNORECASE):
                    if re.search(r'(do|did)\snot\shave', sent[0]):
                        continue
                    if re.search(r'(have|has)\s(no|not|got)', sent[0]):
                        continue
                    else:
                        for trigger in triggers:
                            if re.search(trigger, sent[0]):
                                pp_comment = 'Present Perfect does not go along with indication of past time.'
                                for clause in re.findall(perfect, sent[1]):
                                    perfect_clause = ' '.join(clause)
                                    perfect_clause = re.sub(r'\s\s', ' ', perfect_clause)
                                    perfect_clause = re.sub(r'\sn\'t', 'n\'t', perfect_clause)
                                    if re.search('[a-zA-z]+', perfect_clause):
                                        sent.append([perfect_clause, pp_comment])
                                error_span = re.findall(trigger, sent[0])
                                sent.append([error_span[0][0], pp_comment])
                        # consider that
                if re.search(r'(C|c)onsider\sthat', sent[0]):
                    sent.append([re.findall(r'((?:C|c)onsider\sthat)', sent[0])[0],
                                 'You may have wrongly used the verb CONSIDER with THAT'])
        return data

    def inversion(data):
        start = '(?:<[^>]+?\sV..>)(?:,\sPUN)?(?:<[^>]+?\s(?:AVQ|PNQ|DTQ)>|<[whether|if]\s.+?>)' + \
                '(?:<[^>]+?\sV[B|D|H|M].>)'
        # 1: all verbs, 2: comma, 3: wh-words + whether&if, 4: auxiliaries (be, do, have, modal)
        noun_phrase = nounp()
        verb = '(?:<[^>]+?\sV..>)'
        pattern = start + noun_phrase + verb
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            mis = re.search(pattern, tsent, flags=re.IGNORECASE)
            if mis:
                err = re.findall('<(.+?)\s...>', mis.group())
                error = re.search(err[0] + '.*?' + err[-1], text).group()
                sent.append([error, 'This might me an erroneous use of inversion'])
        return data

    def prepositions(data):
        start = '(?:<[^>]+\s(?:PR.|AVP)>)'
        verbs = open_file('trans.txt').split(', ')
        an_start = '(?:<(?:' + '|'.join(verbs) + ')\s[^N]..>)'
        f_e = '(?:<for\s...><(?:example\s...>))'
        f_i = '(?:<for\s...><(?:instance\s...>))'
        mb = '(?:<maybe\s...>)'
        pr = '(?:<perhaps\s...>)'
        hw = '(?:<however\s...>)'
        psb = '(?:<possibly\s...>)'
        prb = '(?:<probably\s...>)'
        var = '|'.join([f_e, f_i, mb, pr, hw, psb, prb])
        pattern = '(?:' + start + '|' + an_start + ')' + '(?:<,\sPUN>)?' + '(?:' + var + ')' + \
                  '(?:<,\sPUN>)?' + '(' + nounp() + ')'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            for clause in tsent.split('<; PUN>'):
                mis = re.search(pattern, clause)
                if mis:
                    if 'DTQ>' not in mis.groups(1)[0]:
                        err = re.findall('<(.+?)\s...>', mis.group())
                        error = re.search(err[0] + '.*?' + err[-1], text).group()
                        sent.append([error, 'You may have used the wrong word order.'])
        return data

    def conditionals(data):
        fstart = '(?:(?:<if\s...>)' + nounp() + '(?:<(?:will|would)\sV..>|<[^>]+?\sV[VB][BZ]>' + '(?:<[^>]+?\s...>){1,5}' + \
                 '(?:<,\s...>)?' + nounp() + '<would\s...>))'
        sstart = nounp() + '<would\s...>' + '(?:<[^>]+?\s...>){1,6}' + '(?:<[iI]f\s...>)' + nounp() + '<[^>]+?\sV[VB][BZ]>'
        pattern = '(?:' + fstart + ')|(?:' + sstart + ')'
        bad_words = '|'.join(open_file('verbs.txt').split('\n')).lower()
        trg = '<(?:that|because)\s...>(?:<even\s...>)?<if\s...>'
        trg1 = '(?:<[^>]+?\sXX0>)?<(?:' + bad_words + ')\s...>(?:<even\s...>)?<if\s...>'
        trg2 = '<(?:that|who|which)\s...>' + nounp() + '?(?:<[^>]+?\sV..>){1,3}' + '(?:<,\s...>)?' + '(?:<,\s...>)?'
        trg3 = 'would like'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            a = re.search(trg2, tsent, flags=re.IGNORECASE)
            if a:
                text = re.sub(trg2, '', tsent)
            mis = re.search(pattern, tsent, flags=re.IGNORECASE)
            if mis:
                if not (re.search(trg, tsent, flags=re.IGNORECASE) or re.search(trg1, tsent, flags=re.IGNORECASE)
                        or re.search(trg3, text, flags=re.IGNORECASE)):
                    err = re.findall('<(.+?)\s...>', mis.group())
                    error = re.search(err[0] + '.*?' + err[-1], text).group()
                    sent.append([error, 'You may have used the wrong form of the verb in the condition. See more examples at http://realec-reference.site/Conditionals'])
        return data

    def barely(data):
        pattern = '(?:<(?:Barely|Scarcely|Hardly)\s...>)' + nounp() + '(?:<[^>]+\sV..>(?:<[^>]+\s...>){0,4})' + \
                  '(?:<,\s...>)?<when\s...>'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            mis = re.search(pattern, tsent)
            if mis:
                err = re.findall('<(.+?)\s...>', mis.group())
                error = re.search(err[0] + '.*?' + err[-1], text).group()
                sent.append([error, 'Just a reminder that this type of expression requires inversion.'])
        return data

    def had(data):
        pattern = '(?:<Had\s...>)' + nounp() + '(?:<[^>]+\sV.N>(?:<(?:what|whom?|how|where|when|why|if|that|which)+\s...>)?)' + \
                  '<would\s...>' + nounp() + '(?:<[^>]+?\sV[VB][BZ]>|<have\s...><[^>]+\sV.N>)'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            mis = re.search(pattern, tsent)
            if mis:
                err = re.findall('<(.+?)\s...>', mis.group())
                err = ' '.join(err)
                err = re.sub('\s\:\s', ': ', err)
                err = re.sub('\s\;\s', '; ', err)
                err = re.sub('\s\,\s', ', ', err)
                err = re.sub('\sn\'t\s', 'n\'t ', err)
                err = re.sub('\s\s', ' ', err)
                sent.append([err, 'Just a reminder that this type of expression requires inversion.'])
        return data

    def never(data):
        start = '(?:<Never\s...><in\s...><[^>"]+\s...><life\s...>|<Nowhere\s...>(?:<[^>"]+\s...>){0,4}|<Nobody\s...>|<None\s...>|' + \
                '<[^"]+\s...><Nothing\s...>(?:<[^>"]+\s...>){0,4}|<No\s...><one\s...>|<Hardly\s...>|<Barely\s...>|' + \
                '<Scarcely\s...>|<Few\s...>(?:<[^>]+\s...>){0,4})'
        pattern = start + nounp() + '(?:<[^>]+\sV..>)'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            mis = re.search(pattern, tsent)
            if mis and 'Never the less' not in text \
                    and 'Never theless' not in text \
                    and not re.search('Hardly any(?:body|one|thing)?', text) \
                    and 'Hardly a ' not in text:
                err = re.findall('<(.+?)\s...>', mis.group())
                error = re.search(err[0] + '.*?' + err[-1], text).group()
                sent.append([error, 'You may need inverted word order in this sentence.'])
        return data

    def no_sooner(data):
        pattern = '(?:<No\s...><sooner\s...>)' + nounp() + '(?:<[^>]+\sV..>(?:<[^>]+\s...>){0,4})' + '(?:<,\s...>)?<than\s...>'
        for sent in data:
            text = sent[0]
            tsent = sent[1]
            mis = re.search(pattern, tsent)
            if mis:
                err = re.findall('<(.+?)\s...>', mis.group())
                error = re.search(err[0] + '.*?' + err[-1], text).group()
                sent.append([error, 'You may need inverted word order in this sentence.'])
        return data

    def find_punkt_errors(data):

        re_find_b = [r"(From [a-z].? (?:point of view|viewpoint|perspective)).*",
                     r"(From [A-Z][a-z]+'s (?:point of view|viewpoint|perspective)).*", \
                     r'(To [a-z]{2,5} mind)', r'(For (?:example|instance)).*', r'(However|Nevertheless|Consequently|To start with|Firstly| \
    Secondly|Thirdly|Moreover|On the other hand|In other words|In short|Surprisingly| \
    Unsurprisingly|Hopefully|Interestingly|Obviously|In conclusion|To conclude|To sum up| \
    Thus|Of course).*']

        re_check_b = [r'From [a-z]{2,5} (?:point of view|viewpoint|perspective), ',
                      r"From [A-Z][a-z]+'s (?:point of view|viewpoint|perspective), ", \
                      r'To [a-z]{2,5} mind, ', r'For (?:example|instance), ', r'(?:However|Nevertheless|Consequently|To start with|Firstly| \
        Secondly|Thirdly|Moreover|On the other hand|In other words|In short|Surprisingly| \
        Unsurprisingly|Hopefully|Interestingly|Obviously|In conclusion|To conclude|To sum up| \
        Thus|Of course), ']

        re_find_m = [r"\w*? (from [a-z]{2,5} (?:point of view|viewpoint|perspective)).*",
                     r'\w*? (to [a-z]{2,5} mind).*', \
                     r'\w*? (for (?:example|instance)).*', \
                     r'(however|nevertheless|consequently|to start with|firstly|secondly|thirdly|moreover|on the other hand|in other words|in short|surprisingly|\
    unsurprisingly|hopefully|interestingly|obviously|in conclusion|to conclude|to sum up|thus|of course).*']
        re_check_m = [r'.*, from [a-z]{2,5} (?:point of view|viewpoint|perspective), ', r'.*, to [a-z]{2,5} mind, ', \
                      r'.*, for (?:example|instance), ',
                      r'(?:however|nevertheless|consequently|to start with|firstly|secondly|thirdly|moreover|on the other hand|in other words|in short|surprisingly|unsurprisingly|hopefully|interestingly|obviously|in conclusion|to conclude|to sum up|thus|of course), ']
        re_trigger1 = [r'.* (?:вЂ”|-|:) from [a-z]{2,5} (?:point of view|viewpoint|perspective), ',
                       r'.* (?:вЂ”|-|:) to [a-z]{2,5} mind, ', \
                       r'.* (?:вЂ”|-|:) for (?:example|instance), ', r'.* (?:вЂ”|-|:) (?:however|nevertheless|consequently|to start with|firstly| \
        secondly|thirdly|moreover|on the other hand|in other words|in short|surprisingly| \
        unsurprisingly|hopefully|interestingly|obviously|in conclusion|to conclude|to sum up| \
        thus|of course), ']
        re_trigger2 = [r'.*, from [a-z]{2,5} (?:point of view|viewpoint|perspective) (?:вЂ”|-|:|.)',
                       r'.*, to [a-z]{2,5} mind (?:вЂ”|-|:|.) (?:вЂ”|-|:|.)', \
                       r'.*, for (?:example|instance) (?:вЂ”|-|:|.)', r'.*, (?:however|nevertheless|consequently|to start with|firstly| \
        secondly|thirdly|moreover|on the other hand|in other words|in short|surprisingly| \
        unsurprisingly|hopefully|interestingly|obviously|in conclusion|to conclude|to sum up| \
        thus|of course) (?:вЂ”|-|:|.)']

        for sent in data:
            for pattern in re_find_b:
                if re.search(pattern, sent[0]):
                    found = 0
                    for true_pattern in re_check_b:
                        if re.search(true_pattern, sent[0]):
                            found = 1
                            break
                    if found == 0:
                        # print(sent)
                        sent.append([re.findall(pattern, sent[0])[0], 'A comma seems to be missing'])
                    # print(sent)
            for pattern in re_find_m:
                if re.search(pattern, sent[0]):
                    found = 0
                    for true_pattern in re_check_m:
                        if re.search(true_pattern, sent[0]):
                            found = 1
                            break
                    for also_true_pattern in re_trigger1:
                        if re.search(also_true_pattern, sent[0]):
                            found = 1
                            break
                    for also_true_pattern in re_trigger2:
                        if re.search(also_true_pattern, sent[0]):
                            found = 1
                            break
                    if found == 0:
                        sent.append([re.findall(pattern, sent[0])[0], 'A comma seems to be missing'])

        return data

# 23.01.2020
    def find_mistakes_pc(data, pattern, start_exp, recommend):
        for sent in data:
            # text = sent[0]
            tagged_sent = sent[1]
            flag1 = False
            if re.search(pattern, tagged_sent, flags=re.IGNORECASE):
                errexp = [m.group() for m in re.finditer(pattern, tagged_sent, flags=re.IGNORECASE)]
                flag1 = True
            if flag1:
                for err in errexp:
                    long_exp = re.search(start_exp, err, flags=re.IGNORECASE)
                    if long_exp:
                        new_err = re.findall('<(.+?)\s...>', long_exp.group(1))
                        error = ' '.join(new_err)
                        sent.append([error, recommend])
        return data

    def past_con(data):
        # identifying errors in the use of Past Continuous
        # The number /was increasing/ between the years 1700 and 2000.
        # start_exp = was/were(VBD) (+ not/n't XX0?) particip1 (ing)(VBG|VDG|VHG|VVG)

        # often wrongly tagged as AJ0:

        v1 = '(?:<fluctuating\s...>)'
        v2 = '(?:<increasing\s...>)'
        v3 = '(?:<decreasing\s...>)'
        v4 = '(?:<remaining\s...>)'
        v5 = '(?:<rising\s...>)'
        v6 = '(?:<declining\s...>)'

        # add as VVG
        wrong_v = '(?:' + v1 + '|' + v2 + '|' + v3 + '|' + v4 + '|' + v5 + '|' + v6 + ')'

        # rand_words = '(?:<[^>]+\s...>)*'  # сколько угодно либо ни одного

        rand_words2 = '(?:<[^>]+\s...>)*?'  # сколько угодно либо ни одного ОГРАНИЧИЛА ЖАДНОСТЬ!!!
        rand_words_1 = '(?:<[^>]+\s...>)'  # ровно 1 рандом слово

        # кокие-то слова (но мб и без них) + was/were + not/n't(но мб и без) + -ing form of verbs + кокие-то слова (но мб и без них)
        start_exp = rand_words2 + '(' + '(?:<[^>]+\s(?:VBD)>)(?:<[^>]+\s(?:XX0)>)?' + '(?:' + '(?:<[^>]+\s(?:VBG|VDG|VHG|VVG)>)' + '|' + wrong_v + ')' + ')' + rand_words2

        # tagging '1800.'; 1800s
        dig1 = '(?:<1[789][0-9][0-9][^>]+\s...>)'
        dig2 = '(?:<200[0-9][^>]+\s...>)'
        dig3 = '(?:<201[0-8][^>]+\s...>)'

        dig4 = "(?:<1[789][0-9][0-9]\s...>)(?:<'s ...>)?"
        dig5 = "(?:<200[0-9]\s...>)(?:<'s ...>)?"
        dig6 = "(?:<201[0-9]\s...>)(?:<'s ...>)?"

        res_dig = '(?:' + dig1 + '|' + dig2 + '|' + dig3 + '|' + dig4 + '|' + dig5 + '|' + dig6 + ')'

        add_s = '(?:<the\s...>)(?:(?:<end\s...>)|(?:<beginning\s...>)|(?:<start\s...>))(?:<of\s...>)(?:<the\s...)?'

        # 0: in the year [1700-2019]
        # in the?/1 rand_w [1700-2019]
        r0_1 = '(?:<in\s...>)(?:<the\s...>)?(?:<year\s...>)?' + res_dig
        r0_2 = '(?:<in\s...>)' + rand_words_1 + res_dig
        r0 = '(?:' + r0_1 + '|' + r0_2 + ')'

        # 1: between + the years? + [1700-2019] + and + [1700-2019]
        # or between + the beginning of the? + [1700-2019] + and + the start of the? + [1700-2019]
        r1 = '(?:<between\s...>)' + '(?:' + '(?:(?:<the\s...>)(?:<years\s...>))?' + '|' + '(?:' + add_s + ')?' + ')' + res_dig + '(?:<and\s...>)' + '(?:' + add_s + ')?' + rand_words_1 + '?' + res_dig

        # 2: from + the year? + [1700-2019] + to + [1700-2019]
        r2 = '(?:<from\s...>)' + '(?:' + '(?:(?:<the\s...>)(?:<year\s...>))?' + '|' + '(?:' + add_s + ')?' + ')' + res_dig + '(?:<to\s...>)' + '(?:' + add_s + ')?' + rand_words_1 + '?' + res_dig
        # 2_1:
        # from n till/until n
        # until/till rw? numb

        r2_1_1 = '(?:<from\s...>)' + rand_words_1 + '?' + res_dig + '(?:' + '(?:<till\s...>)' + '|' + '(?:<until\s...>)' + ')' + rand_words_1 + '?' + res_dig
        r2_1_2 = '(?:' + '(?:<until\s...>)' + '|' + '(?:<till\s...>)' + ')' + rand_words_1 + '?' + res_dig

        r2_1 = '(?:' + r2_1_1 + '|' + r2_1_2 + ')'

        # 3: at|in|during + the + first|second|third|fourth|fifth|initial|last + stage|point|phase|period
        r3 = '(?:(?:<at\s...>)|(?:<in\s...>)|(?:<during\s...>))' + '(?:' + '(?:' + add_s + ')?' + '|' + '((?:<the\s...>)(?:(?:<first\s...>)|(?:<second\s...>)|(?:<third\s...>)|(?:<fourth\s...>)|(?:<fifth\s...>)|(?:<initial\s...>)|(?:<last\s...>))?)' + ')' + '(?:(?:<stage\s...>)|(?:<point\s...>)|(?:<phase\s...>)|(?:<period\s...>)|(?:<century\s...>)|(?:<decade\s...>)|(?:<year\s...>)|(?:<month\s...>))'

        # 4: from year to year     during this/(all the) period/year(s)/stage/century   during these periods/years/stages  through the years
        r4_4 = '(?:<from\s...>)(?:<year\s...>)(?:<to\s...>)(?:<year\s...>)'
        r4_2 = '(?:<during\s...>)' + '(?:' + '(?:<this\s...>)' + '|' + '(?:(?:<all\s...>)(?:<the\s...>))' + ')' + '(?:' + '(?:<year\w\s...>)' + '|' + '(?:<period\s...>)' + '|' + '(?:<stage\s...>)' + '|' + '(?:<century\s...>)' + '|' + '(?:<month\s...>)' + ')'
        r4_3 = '(?:<during\s...>)' + '(?:' + '(?:<these\s...>)' + '|' + '(?:<those\s...>)' + ')' + '(?:' + '(?:<years\s...>)' + '|' + '(?:<periods\s...>)' + '|' + '(?:<stages\s...>)' + ')'
        r4_1 = '(?:<through\s...>)(?:<the\s...>)(?:<years\s...>)'
        r4 = '(?:' + r4_1 + '|' + r4_2 + '|' + r4_3 + r4_4 + ')'
        contin_exp = '(?:' + r0 + '|' + r1 + '|' + r2 + '|' + r3 + '|' + r4 + '|' + r2_1 + ')'

        # ошибка в starte цифры в конце
        # np + was/were + not/n't? + ing + from N to N
        full_exp_stm = start_exp + contin_exp

        # а теперь цифры в начале ошибка в конце
        # between N and N + np + was/were + not/n't? + ing
        full_exp_finm = contin_exp + start_exp

        # оба этих случая
        pattern = '(?:' + full_exp_stm + '|' + full_exp_finm + ')'

        recommend = 'The usage of Past Continuous might be erroneous'
        data_for_return = find_mistakes_pc(data, pattern, start_exp, recommend)
        return data_for_return

####################

    def find_com_mistakes(data, pattern, recommend):

        cth = '(<, PUN><that\s...>)<([^>]+)\s....?>'
        punc = '(?:<[^>]+\sPU.>)'
        sent_end = '(?:<[^>]+\sSENT>)'
        rand_words_no_pun_not_obl = '(?:<[^>]+\s[^V][^U].>)*'
        cif = '(<if\s...>)' + rand_words_no_pun_not_obl + '<[^>]+\sV..>' + rand_words_no_pun_not_obl + '(?:' + punc + '|' + sent_end + ')'

        for sent in data:
            text = sent[0]
            tagged_sent = sent[1]
            flag1 = True
            errexp = re.findall(pattern, tagged_sent, flags=re.IGNORECASE)  # !
            if len(errexp) > 0:
                for err in errexp:
                    mis = re.search(cth, err, flags=re.IGNORECASE)
                    long_exp = re.search(cif, err, flags=re.IGNORECASE)
                    if mis:
                        if mis.group(2) == 'is' or mis.group(2) == "'s":
                            errexp.remove(err)
                            if len(errexp) == 0:
                                flag1 = False
                        else:
                            new_err = re.sub(mis.group(), mis.group(1), err)

                            errexp.remove(err)
                            errexp.append(new_err)
                    elif long_exp:
                        # Р·Р°РјРµРЅСЏРµС‚ РІ РѕС€РёР±РєРµ if РєР°РєРѕРµ-С‚Рѕ СЃР»РѕРІРѕ + РіР»Р°РіРѕР» +... РЅР° РїСЂРѕСЃС‚Рѕ if
                        new_err = re.sub(long_exp.group(), long_exp.group(1), err)

                        errexp.remove(err)
                        errexp.append(new_err)
                if flag1:
                    for el in errexp:
                        new_err2 = re.findall("<(.+?)\s...>", el)
                        error = re.search(new_err2[0] + ".*?" + new_err2[-1], text).group()
                        errexp.remove(el)
                        errexp.append(error)
                    errexp.append(recommend)
                    sent.append(errexp)  # !
        return data

    def extra_comma(data):
        # He did not know, why she said it.

        rand_words_no_pun = '(?:<[^>]+\s.[^U].>)+'

        rand_words_no_pun_not_obl = '(?:<[^>]+\s.[^U].>)*'

        comma = '(?:<, PUN>)'
        punc = '(?:<[^>]+\sPU.>)'
        sent_end = '(?:<[^>]+\sSENT>)'

        conj_that = '<that\s...><[^>]+\s....?>'

        conj_if = '<if\s...>' + rand_words_no_pun_not_obl + '<[^>]+\sV..>' + rand_words_no_pun_not_obl + '(?:' + punc + '|' + sent_end + ')'

        conj = '(?:' + '(?:<what\s...>)' + '|' + '(?:<how\s...>)' + '|' + '(?:<why\s...>)' + \
               '|' + '(?:<where\s...>)' + '|' + '(?:<when\s...>)' + '|' + '(?:<whether\s...>)' + ')'

        conj_choice = '(?:' + conj_that + '|' + conj_if + '|' + conj + ')'

        verb = '(?:<[^>]+\sV..>)'

        main_clause_c = nounp() + rand_words_no_pun + verb + comma + conj_choice

        # It is obvious/evident comma that
        # It is worth + noticing/saying/mentioning/reminding/discussing + comma  + that

        r0 = '(?:<it\s...>)(?:<is\s...>)'
        r1 = '(?:<worth\s...>)'
        r2 = '(?:' + '(?:<obvious\s...>)' + '|' + '(?:<evident\s...>)' + '|' + '(?:<clear\s...>)' + ')'

        r3 = '(?:' + '(?:<noticing\s...>)' + '|' + '(?:<saying\s...>)' + '|' + '(?:<mentioning\s...>)' + '|' + '(?:<reminding\s...>)' + \
             '|' + '(?:<discussing\s...>)' + ')'

        res0 = r0 + r1 + r3 + comma + '(?:<that\s...>)'
        res1 = r0 + r2 + comma + '(?:<that\s...>)'

        res_i = '(?:' + res0 + '|' + res1 + ')'
        pattern = '(?:' + res_i + '|' + main_clause_c + ')'

        recommend = 'You may have used a redundant comma in this sentence.'
        data_for_return = find_com_mistakes(data, pattern, recommend)

        return data_for_return

    def gerund(data):
        """ 1) check if one of the gerunds is in the sentence at all (the gerunds are in file mistake_if_followed_by_of.txt)
            2) check if it is followed by of (not off)
            3) append ['gerund of', 'comment] to the sent in data
        """
        with open('mistake_if_followed_by_of.txt', 'r', encoding='utf-8') as file:
            raw = file.read()
            gerunds = raw.split()

        for sent in data:
            text = sent[0]
            sent_pos = sent[1]
            for gerund in gerunds:
                if gerund in text:
                    pattern = gerund + ' of '
                    mis = re.search(pattern, text)
                    if mis:
                        sent.append([pattern, 'This gerund needs direct object'])
        return data



    def output_maker(data):
        output = []
        for sent in data:
            mistakes = []
            already_mentioned = []
            original = sent[0]
            error_spans = sent[2:]
            for error_span in error_spans:
                if error_span[0] not in already_mentioned:
                    mistakes.append([error_span[0], error_span[1]])
                    already_mentioned.append(error_span[0])
                else:
                    continue

            for i in mistakes:
                subst = '@[' + i[0] + 'COMMENT' + i[1] + ']@'
                original = re.sub(i[0], subst, original)
            for i in original.split('@'):
                if i.startswith('['):
                    error_span = (re.sub('\[|\]', '', i)).split('COMMENT')[0]

                    comment = (re.sub('\[|\]', '', i)).split('COMMENT')[1]
                    annotation = []
                    annotation.append(error_span)
                    annotation.append("1")
                    annotation.append(comment)
                    if annotation[0] != '':
                        output.append(annotation)

                else:
                    annotation = []
                    annotation.append(i)
                    annotation.append("0")
                    annotation.append("")
                    if annotation[0] != '':
                        output.append(annotation)
        return output

    ## for the sake of having a list of models on display
    text = user_input
    data = preprocessing(text)
    data = pp_time(data)
    data = inversion(data)
    data = prepositions(data)
    data = conditionals(data)
    data = barely(data)
    data = had(data)
    data = never(data)
    data = no_sooner(data)
    data = extra_comma(data)
    data = past_con(data)
    data = find_punkt_errors(data)
    data = gerund(data)
    output = output_maker(data)

    return output


def main():
    user_input = 'First of all, we need to know why did the level of crime boost up In the period of 12 years (from 2000 to 2012) statistic has been changed a lot.'

    m = models(user_input)
    print(m)



if __name__ == '__main__':
    main()
