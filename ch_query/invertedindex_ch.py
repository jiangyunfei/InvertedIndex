#! -*- coding:utf-8 -*-
import os
import glob
import string
import re



class InvertedIndex:
    def __init__(self,DATA_path, DICT_path, SW_path):
        #Get raw data
        extension_list = ['txt']
        flist = self.get_file_list(DATA_path,extension_list)
        self.data = self.get_file_txt(flist)

        self.K = 5 #settting for proximity search
        self.STOP_WORDS = self.get_ch_STOPWORDS(SW_path)

        #Convert to dict
        self.ch_dict = self.get_ch_dict(DICT_path)
        self.words_dict = self.data2dict(self.data)

        for k,v in self.words_dict.items():
            print k, ':', v, '\n'
        print('Ready to query.')

    def get_file_list(self, dir_path, extension_list):
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
            file_list += [os.path.realpath(e) for e in glob.glob(extension)]
        return file_list

    def get_file_txt(self,file_path_list):
        data = {}
        for file_path in file_path_list:
            file = open(file_path)
            txt = file.read()

            tmp = file_path.split('/')
            file_name = tmp[-1]

            data[file_name]=txt

            #print(file_name)
            #print('-'*10)
            #print(txt+'\n')
            file.close()

        return data

    ####DATA2DICT####
    def get_ch_STOPWORDS(self,sw_path):
        tmp = sw_path.split('/')
        os.chdir('../'+tmp[0])
        dict_file_path=os.path.realpath(tmp[1])

        file = open(dict_file_path)
        dict = []
        while True:
            line = file.readline()
            line = line.replace('\n', '')
            if not line:
                break;

            dict.append(unicode(line,'utf8'))

        file.close()
        print('STOPWORDS: '+str(len(dict))+' words.')
        return dict

    def get_ch_dict(self,DICT_path):
        tmp = DICT_path.split('/')
        os.chdir('../'+tmp[0])
        dict_file_path=os.path.realpath(tmp[1])

        file = open(dict_file_path)
        dict = []
        while True:
            line = file.readline()
            if not line:
                break;

            tmp = line.split()
            dict.append(unicode(tmp[0],'utf8'))

        file.close()
        print('Dict: '+str(len(dict))+' words.')
        return dict


    def seg_ch_words(self,ch_txt):
        seg_list = []
        max_len = 5
        ptr = 0
        str_len = len(ch_txt) #begin at 0

        while ptr < str_len:
            is_add = False
            l = max_len

            if (str_len-ptr) < max_len:
                l = str_len - ptr

            for i in range(l):
                s = ch_txt[ptr:ptr+l-i]

                if s in self.ch_dict:
                    seg_list.append(s)
                    ptr = ptr+len(s)
                    is_add = True
                    break

            #single
            if not is_add:
                s = ch_txt[ptr:ptr+1]
                seg_list.append(s)
                ptr = ptr+len(s)
                is_add = True

            #print('SEG s='+s)

        #for x in seg_list:print x
        return seg_list


    def txt_preprocessing(self,_txt):
        txt = _txt.strip()
        txt = txt.translate(None, string.punctuation) #remove those things we don't like
        txt = txt.replace('\t','') #remove '\t'
        txt = txt.replace('\n','') #remove '\n'
        txt_utf8 = txt.decode('utf8')

        str = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),txt_utf8)

        return str


    def txt2position(self,seg_ch_words):
        pos_dict = {}
        idx = 0
        for word in seg_ch_words:
            idx = idx+1
            if word in self.STOP_WORDS:
                print('STOPW: '+word)
                continue

            pos = []

            if word in pos_dict:
                pos = pos_dict[word]

            pos.append(idx)
            pos_dict[word]=pos
            print('ADD KEY: '+word)

        return pos_dict


    def update_words_dict(self,wd,pd,docID):

        for word,pos in pd.items():
            tmp_dict = {}
            if word in wd:
                tmp_dict = wd[word]

            tmp_dict[docID]=pos
            wd[word]=tmp_dict


    def data2dict(self,data):
        '''
        convert txt data to dictionary and postings
        '''
        words_dict = {}
        for docID,txt in data.items():
            txt = self.txt_preprocessing(txt)
            #print ('RAW: '+txt)
            print '-> ', docID, ":", txt, '\n'

            seg_ch_words = self.seg_ch_words(txt)
            pos_dict = self.txt2position(seg_ch_words)

            self.update_words_dict(words_dict,pos_dict,docID)


        return words_dict

    ###SEARCH###
    def print_results(self,weight,datas):
        print('\n'+'*'*20+'\n')
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

    def caculate_weights(self, words, docIDs, results_data,results_weight):
        for id in docIDs:
            result = {}
            word_pos = []
            for word in words:
                pos_dict = self.words_dict[word]
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
                elif sub < self.K:
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

    def search_words(self,key):

        if len(key)==1:
            seg_list = self.seg_ch_words(key[0])
            if len(seg_list)==1:
                w = seg_list[0]
                if w in self.words_dict:
                    postings = self.words_dict[w]
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

        docs = []
        words = []
        for k in key:
            words_seg = self.seg_ch_words(k)

            for word in words_seg:
                if word in self.words_dict:
                    pos_dict = self.words_dict[word]
                    docs.append(pos_dict.keys())
                    words.append(word)
                    print('SEG s='+word)
                else:
                    if word in self.STOP_WORDS:
                        print('SEG s='+word+'(STOPWORDS)')
                    else:
                        print('SEG s='+word+'(None)')

                        return False

        docIDs = docs[-1]
        for doc in docs:
            docIDs = list(set(docIDs) & set(doc))
            if len(docIDs) == 0:
                return False

        results_data = {}
        results_weight = {}

        self.caculate_weights(words,docIDs,results_data,results_weight)

        self.print_results(results_weight, results_data)
        return True

    def search(self):
        print('*'*20 + '\n')
        print('Inverted Index CHS, designed by Jiang Yunfei@BUPT\n')
        flag = True
        while flag:
            key = raw_input('-> Search:')
            key = key.split()
            key = [unicode(k, 'utf-8') for k in key]

            re = self.search_words(key)

            if re == False:
                print '\n[ALERT] Nothing found!'

            usr = raw_input('Do you want to query again?(y/n)')
            if usr =='n':
                flag = False




if __name__ == '__main__':
    #TEST
    data_path='DATA_CHS'
    dict_path='CH_DICT/dict.txt'
    stopwords_path = 'CH_DICT/sw.txt'
    ii = InvertedIndex(data_path,dict_path,stopwords_path)
    ii.search()


