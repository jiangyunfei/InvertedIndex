import os
import glob
import string

K = 5 #settting for proximity search

STOP_WORDS = frozenset([
'a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again',
'against', 'all', 'almost', 'alone', 'along', 'already', 'also','although',
'always','am','among', 'amongst', 'amoungst', 'amount',  'an', 'and', 'another',
'any','anyhow','anyone','anything','anyway', 'anywhere', 'are', 'around', 'as',
'at'])


def get_file_list(dir_path, extension_list):
    '''
    fuction: get_file_list(dir_path,extension_list)
    parms:
    dir_path - a string of directory full path. eg. 'D:user'
    extension_list - a list of file extension. eg. ['zip']
    return: a list of file full path. eg. ['D:user1.zip', 'D:user2.zip']
    '''
    os.chdir(dir_path)
    file_list = []
    for extension in extension_list:
        extension = '*.' + extension
        file_list += [os.path.realpath(e) for e in glob.glob(extension) ]
    return file_list


def get_file_txt(file_path_list):
    data = {}
    for file_path in file_path_list:
        file = open(file_path)
        txt = file.read()

        tmp = file_path.split('/')
        file_name = tmp[-1]

        data[file_name]=txt

        print(file_name)
        print('-'*10)
        print(txt+'\n')

    return data

####DATA2DICT####

def txt_preprocessing(_txt):
    txt = _txt.strip()
    txt = txt.translate(None, string.punctuation) #remove those things we don't like
    txt = txt.replace('\t','') #remove '\t'
    txt = txt.replace('\n','') #remove '\n'
    return txt


def txt2position(txt):
    pos_dict = {}
    idx = 0
    for word in txt.split():
        idx = idx+1
        if word in STOP_WORDS:
            continue

        pos = []

        if word in pos_dict:
            pos = pos_dict[word]

        pos.append(idx)
        pos_dict[word]=pos

    return pos_dict


def update_words_dict(wd,pd,docID):

    for word,pos in pd.items():
        tmp_dict = {}
        if word in wd:
            tmp_dict = wd[word]

        tmp_dict[docID]=pos
        wd[word]=tmp_dict


def data2dict(data):
    '''
    convert txt data to dictionary and postings
    '''
    words_dict = {}
    for docID,txt in data.items():
        txt = txt_preprocessing(txt)
        pos_dict = txt2position(txt)
        update_words_dict(words_dict,pos_dict,docID)

        print docID, ":", txt, '\n'

    return words_dict

###SEARCH###

def search_single_word(wd,key):

    if key in wd:
        postings = wd[key]
        weights = {}
        results_data = {}
        for id,pos in postings.items():
            weight = len(postings[id])
            weights[id]=weight

        i=0
        for id in sorted(weights, key=weights.get, reverse=True):
            i=i+1
            print('Rank'+str(i)+': '+ id + '\n'+'-'*20)
            print('weight: '+str(weights[id]))
            print('Pos: '+str(postings[id]))
            print('\n')

        return True
    else:
        return False


def print_results(weight,datas):
    i = 0
    for id in sorted(weight, key=weight.get, reverse=False):
        data = datas[id]
        i=i+1
        print('Rank'+str(i)+': '+ id + '\n'+'-'*20)
        print('weight: '+str(data['weight']))
        print('Pos: '+str(data['pos']))
        if data['isPhrase']:
            print('Hint: find phrase')
        elif data['isProximity']:
            print('Hint: proximity search within 5 words')
        else:
            print('Hint: just in the same document')

        print('\n')

def caculate_weights(wd,words,docIDs,results_data,results_weight):
    for id in docIDs:
        result = {}
        word_pos = []
        for word in words:
            pos_dict = wd[word]
            #word_pos.append(pos_dict[id])
            word_pos = word_pos + pos_dict[id]

        word_pos.sort()

        m = len(word_pos)
        sub_pos = []
        isPhrase = False
        isProximity = False
        for i in range(m-1):
            sub = word_pos[i+1]-word_pos[i]
            if sub ==1:
                isPhrase = True
            elif sub < K:
                isProximity = True
            sub_pos.append(sub)

        weight=sum(sub_pos)/len(sub_pos) #caculate the weight for every result

        result['id']=id
        result['pos']=word_pos
        result['weight']=weight
        result['isPhrase']=isPhrase
        result['isProximity']=isProximity

        results_data[id]=result
        results_weight[id]=weight


def search_words(wd,key):
    words = key.split()
    docs = []
    dicts = []
    for word in words:
        if word in wd:
            pos_dict = wd[word]
            docs.append(pos_dict.keys())
        else:
            return False

    m =len(words)
    docIDs = docs[-1]
    for doc in docs:
        docIDs=list(set(docIDs) & set(doc))
        if len(docIDs)==0:
            return False

    results_data = {}
    results_weight = {}

    caculate_weights(wd,words,docIDs,results_data,results_weight)

    print_results(results_weight,results_data)
    return True


def search(wd,key):
    if len(key.split())==1:
        re = search_single_word(wd,key)
    else:
        re = search_words(wd,key)

    if re == False:
        print '[ALERT] Nothing found!'



if __name__ == '__main__':
    #Test
    dir_path='DATA'
    extension_list=['txt']
    X = get_file_list(dir_path,extension_list)
    data = get_file_txt(X)
    print('*'*20)
    wd = data2dict(data)
    for k,v in wd.items():
        print k, ':', v, '\n'

    print('*'*20 + '\n')
    print('Inverted Index, designed by Jiang Yunfei@BUPT\n')
    key = raw_input('-> Search:')
    print('...\n')

    search(wd,key)
