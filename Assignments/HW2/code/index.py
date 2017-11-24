 #! user/bin/python
import re, os, timeit, time, operator
from nltk.stem.porter import *
##from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

##STOPLIST = stopwords.words('english')
##print len(STOPLIST)
stemmer = PorterStemmer()

FILEPATH = '/Users/xinshu/desktop/CS6200/DATA/AP_DATA/ap89_collection/'
INDEXPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW2/tempindex/'
CATALOGPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW2/catalog/'
DOC_LEN = '/Users/xinshu/desktop/CS6200/Assignments/HW2/doc_len'
DOC_ID = '/Users/xinshu/desktop/CS6200/Assignments/HW2/doc_id'
STOP_LST = '/Users/xinshu/desktop/CS6200/Assignments/HW2/stoplist'

doc_no = 0
STOPLIST = []

def main():
    start = timeit.default_timer()
    
    open_stopwords_file()
    open_filelist()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60),)

def open_stopwords_file():
    file = open(STOP_LST, "r")
    l = file.readline()

    while l:
        l = file.readline()[:-1]
        STOPLIST.append(l)
        
def open_filelist():
    dcount = 0
    filenamelist = os.listdir(FILEPATH)
    
    for f in filenamelist:
        if 'ap' not in f:
            print f
            continue
        filepath = FILEPATH + f
        readFile(filepath, f)
        dcount += 1
        print (dcount, f)
        
def readFile(filepath, filename):
    fh = open(filepath, "r")
    l = fh.readline()
    global doc_no
    index_map = {}
    doclen = {}
    doc_id_map = {}

    while l:
        while l and '<DOC>' not in l:
             l = fh.readline()
        while l and 'DOCNO' not in l:
            l = fh.readline()
        
        doc_id = l.split()[1]
        while l and '<TEXT>' not in l:
            l = fh.readline()
        text = ''
        while l and '<TEXT>' in l:
            l = fh.readline()
            while l and '</TEXT>' not in l:
                text += l
                l = fh.readline()
            while l and '<TEXT>' not in l and '<DOC>' not in l:
                l = fh.readline()
            if l and '<TEXT>' in l:
                continue
            else:
                break

        text = tokenizer(text)
        text = remove_stopwords(text)
        text = stem_words(text)
        

        if len(text) != 0:
            doclen[doc_id] = len(text)
            doc_id_map[doc_no] = doc_id
            text = count_tf_pos(text, doc_no)
            doc_no += 1
            addto_index_map(text, index_map)         

    writeFile(filename, index_map)
    writeDocLen(doclen)
    writeDocId(doc_id_map)
    fh.close()
    
    
def tokenizer(text):
##    textlist = word_tokenize(text.lower())
##    textlist = re.findall(r"\w+(?:\.?\w+)*", text.lower())
    textlist = re.findall(r'\w+(?:\.\w+)*', text.lower())
    return textlist

def remove_stopwords(text):
    textlist = []
    for word in text:
        if word not in STOPLIST:
            textlist.append(word)
    return textlist

def stem_words(text):
    stemwords = []
    for word in text:
        newword = stemmer.stem(word)
        stemwords.append(newword)
    return stemwords

def count_tf_pos(termlist, doc_id):
    pos = 0
    terms = {}
    for word in termlist:
        if word in terms:
            terms[word]['tf'] += 1
            terms[word]['pos'].append(pos)                   
        else:
            terms[word]={'doc_id': doc_id, 'tf': 1, 'pos': [pos]}
        pos += 1
    return terms

def addto_index_map(termlist, index_map):
    for word, doc_lst in termlist.iteritems():
        if word in index_map:
            index_map[word].append(doc_lst)
        else:
            index_map[word] = [doc_lst]

def writeFile(filename, index_map):
    """
    create the index and catalog file. The index file store the index_dict which is an inverted list
    the catalog file store the begin position and length of each term in index file bytes
    The index file format is id tf poses, which poses seperate by ","
    """
    index_output = INDEXPATH + filename
    catalog_output = CATALOGPATH + filename
    index_f = open(index_output, "w")
    cata_f = open(catalog_output, "w")
    begin_pos = 0
    
    for word in sorted(index_map):
        tmplist = []
        tmplist.append(word)

        index_map[word] = sorted(index_map[word], key=lambda x: x['tf'], reverse=True)
        for doc in index_map[word]:
            
            pos_string = ",".join(map(str, doc['pos']))
            tmplist.extend([str(doc['doc_id']), str(doc['tf']), pos_string])

        postinglist = " ".join(tmplist)
        postinglist = postinglist + "\n"
        offset = len(postinglist)
        index_f.write(postinglist)
        cata_f.write('%s %d %d\n'%(word, begin_pos, offset))
        begin_pos += offset
    index_f.close()
    cata_f.close()

def writeDocLen(doclen):
    fh = open(DOC_LEN, "a")
    for doc_id, length in doclen.iteritems():
        fh.write('%s %d\n'%(doc_id, length))
    fh.close()

def writeDocId(doc_id_map):
    fh = open(DOC_ID, "a")
    for id, doc_id in doc_id_map.iteritems():
        fh.write('%d %s\n'%(id, doc_id))
    fh.close()

if __name__ == '__main__':
    main()
    
