#!/user/bin/python
from __future__ import division
import os, re, timeit
import models
from nltk.stem.porter import *

stemmer = PorterStemmer()

QUERYFILE='/Users/xinshu/desktop/CS6200/DATA/AP_DATA/query_desc.51-100.short.txt'
QUERYPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW2/temp'

TEST_TF = '/Users/xinshu/desktop/CS6200/Assignments/HW2/in.0.50.txt'
STEMMED_TF_OUTPUT = '/Users/xinshu/desktop/CS6200/Assignments/HW2/out.0.stop.stem.txt'
TF_OUTPUT = '/Users/xinshu/desktop/CS6200/Assignments/HW2/out.0.no.stop.no.stem.txt'
STEM_RES_TF = '/Users/xinshu/desktop/CS6200/Assignments/HW2/stem_res_tf.txt'
RES_TF = '/Users/xinshu/desktop/CS6200/Assignments/HW2/res_tf.txt'

def main():
    start = timeit.default_timer()
    
    m = models.QueryModel()
    get_tf(m)
##    run_models(m) # run 5 function models and proximity search

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60),)

def run_models(m):
    """
    get the query dictionary, calculate the model function for each query
    :param m: QueryModel class
    """
    querys = getQuerys()
    
    for no, query in querys.iteritems():
##        m.models(no, query)
        m.proximity_model(no, query)

def getQuerys():
    """
    read the query file and get the query number and useful content, tokenize them by different index type
    :param type: index type
    :return: list of query number and a query content dictionary
    """
    fh=open(QUERYFILE,"r")
    querys=fh.readlines()
    new_querys = {}
    
    for query in querys:
        print query
        new_query = query[:-1].split(" ")[1:]
        new_querys[queryno] = new_query
        
    fh.close()
    return new_querys


def get_tf(m):
    fh = open(TEST_TF, 'r')
    
    word_dic = {}
##    res_dic = read_res_tf()
    words = fh.readlines()
    
    for word in words:        
        word = word[:-1]
        newword = stemmer.stem(word)
        print newword
        df, tf, _, sumtf, pos_dic = m.getTF(newword)
##        word_dic[word] = [df, sumtf, newword]
        print ("df: ", df, "sumtf: ", sumtf)
        for doc_id, doc_tf in tf.iteritems():
            if doc_id in pos_dic.keys():
                print (doc_id, doc_tf, pos_dic[doc_id])
        

    fh.close()
##    compare_tf(word_dic, res_dic)

def compare_tf(word_dic, res_dic):
    count = 0
    wrong = 0
    for word, lst in word_dic.iteritems():
        df = lst[0]
        ttf = lst[1]
        
        if word in res_dic.keys():
            res = res_dic[word]
            res_df = int(res[0])
            res_ttf = int(res[1])
            
            if res_df != df or res_ttf != ttf:
                print (word, df, res_df, ttf, res_ttf, lst[2])
                wrong +=1             
            else:
                count += 1
        else:
            print ('no word in res_tf: ', word)
            
    precision = count/(wrong + count)           
    print ('precision: ', precision) 

def read_res_tf():
##    result = open(RES_TF, 'r')
    result = open(STEM_RES_TF, 'r')
    res_dic = {}
    res = result.readlines()

    for l in res:
        l = l[:-1].split(' ')
        w = l[0]
        df = l[1]
        ttf = l[2]
        res_dic[w] = [df, ttf]
        
    return res_dic


if __name__ == '__main__':
    main()
