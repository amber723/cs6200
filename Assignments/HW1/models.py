#!/user/bin/python
from __future__ import division
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
import os, sys, math, operator, time, json

INDEX = 'ap_dataset'
DOC_TYPE = 'document'
QUERY_TYPE = 'query'
OUTPATH = '/Users/xinshu/desktop/CS6200/DATA/result/'

es=Elasticsearch()

class QueryModel:
    """
    This class calculate IR models
    """
    def __init__(self, client, index, doc_type):
        self.client = client
        self.index = index
        self.doc_type = doc_type

        self.doc_dic = self.getDocDic()
        self.avgd = self.getAvgLen()
        self.vsize = self.getVsize()
        self.outputPath = OUTPATH
        
        print "The total number of docs is: " + str(self.count)
        print "The average length of docs is: " + str(self.avgd)
        print "The vocabulary size is: " + str(self.vsize)

    def getDocDic(self):
        doc_len_dict = {}
        body={
            "query": {
                "match_all": {}
            }
        }       
        doc = self.client.search(index=self.index, doc_type=self.doc_type,
                                 body=body, explain=False, scroll="100m",size=100)
        self.count = doc['hits']['total']
        while len(doc['hits']['hits']) > 0:
            scrollId= doc['_scroll_id']
        
            for i in doc['hits']['hits']:
                doc_len = i['_source']['doc_l']
                doc_no = i['_source']['docno']
                if doc_len > 0:
                    doc_len_dict[doc_no] = doc_len

            doc = self.client.scroll(scroll_id = scrollId, scroll='1000ms')

        return doc_len_dict

    def getAvgLen(self):
        body={
            "aggs": {
                "avg_docs_l": {
                    "avg": {
                        "script": "doc['doc_l'].values"
                    }
                }
            }
        }       
        aggs = es.search(index=self.index, doc_type=self.doc_type, body=body)
        avglen = aggs['aggregations']['avg_docs_l']['value']
        return avglen

    def getVsize(self):
        body = {
            "aggs": {
                "unique_terms": {
                    "cardinality": {
                        "script": "doc['text'].values"
                    }
                }
            }
        }
        unique_terms = self.client.search(index=self.index, doc_type=self.doc_type,body=body)
        vsize = unique_terms['aggregations']['unique_terms']['value']
        return vsize

    def getTF(self, term, term_o):
        """
        Use the elasticsearch query to get a word frequency
        :param term: search word
        :return: df, a dictionary of tf, the sum of doc length
         where has the word, the sum of frequency
        """
        body={
          "_source": "docno",
          "query": {
             "match": {
               "text": term_o
             }
          },
          "script_fields": {
            "tf":{
              "script":{
                "lang": "groovy",
                "inline": "_index['text'][term].tf()",
                "params": {
                  "term":term
                }
              }
            },
            "ttf":{
              "script":{
                "lang": "groovy",
                "inline": "_index['text'][term].ttf()",
                "params": {
                  "term":term
                }
              }
            } 
          }
        }

        resp = self.client.search(index=self.index, doc_type=self.doc_type,
                                  body=body, explain=False, scroll="100m",size=100)          
        tf = {}
        sum_doclen = 0
        ttf = 0
        
        if len(resp['hits']['hits']) > 0:
            df = resp['hits']['total']
            ttf = sum(resp['hits']['hits'][0]['fields']['ttf'])
        else:
            return 0, tf, sum_doclen, ttf

        j = 0
        while len(resp['hits']['hits']) > 0:
            scrollId= resp['_scroll_id']
        
            for i in resp['hits']['hits']:
                doc_no = i['_source']['docno']
                tf_i = sum(i['fields']['tf']) 
                tf[doc_no] = tf_i
                doc_len = self.doc_dic[doc_no]
                sum_doclen += doc_len
                j+=1

            resp = self.client.scroll(scroll_id = scrollId, scroll='1000ms')

        for doc_no in self.doc_dic.keys():
            if doc_no not in tf:
                tf[doc_no] = 0
                
##        print ('df: ', j, df, 'ttf: ', ttf)
        return df, tf, sum_doclen, ttf


    def models(self,query,query_num):
        """
        give a query and calculate the score using five models,
        which are okapiTF, TFiDF, okapiBM25, LM_laplace and LM_jm.
        and write the first 1000 result to the file
        :param query: a dictionary contains word and it frequency
        :param query_num: the query num
        """
        okapi_tf_sigma = {}
        tf_idf_sigma = {}
        bm25_sigma = {}
        lm_laplace = {}
        lm_jm = {}
        query_len = len(query)
        lam = 0.5
        
        for word, word_o in query.iteritems():
            df, tfs, sumlen, sumtf= self.getTF(word, word_o)
           
            for doc_no, tf in tfs.iteritems():
                doc_len = self.doc_dic[doc_no]
                
##                okapi_tf = self.okapiTF(tf, doc_len)
##                tf_idf = self.tfiDF(okapi_tf, df)
##                bm25 = self.okapiBM25(tf, doc_len, df)
##                log_p_laplace = self.lm_laplace(tf, doc_len)
                log_p_jm = self.lm_jm(tf, doc_len, sumtf, sumlen, lam)
                
                if doc_no in okapi_tf_sigma:
##                if doc_no in lm_jm:
                    okapi_tf_sigma[doc_no] += okapi_tf 
                    tf_idf_sigma[doc_no] += tf_idf
                    bm25_sigma[doc_no] += bm25
                    lm_laplace[doc_no] += log_p_laplace
                    lm_jm[doc_no] += log_p_jm
                else :
                    okapi_tf_sigma[doc_no] = okapi_tf 
                    tf_idf_sigma[doc_no] = tf_idf
                    bm25_sigma[doc_no] = bm25
                    lm_laplace[doc_no] = log_p_laplace
                    lm_jm[doc_no] = log_p_jm
            
##        sorted_okapi_tf_sigma = sorted(okapi_tf_sigma.items(), key=operator.itemgetter(1), reverse = True)
##        sorted_tf_idf_sigma = sorted(tf_idf_sigma.items(), key=operator.itemgetter(1), reverse = True)
##        sorted_bm25_sigma = sorted(bm25_sigma.items(), key=operator.itemgetter(1), reverse = True)
##        sorted_lm_laplace = sorted(lm_laplace.items(), key=operator.itemgetter(1), reverse = True)
        sorted_lm_jm = sorted(lm_jm.items(), key=operator.itemgetter(1), reverse = True)
        
##        self.writeFile("okapitf", query_num, sorted_okapi_tf_sigma)
##        self.writeFile("tfidf", query_num, sorted_tf_idf_sigma)
##        self.writeFile("bm25", query_num, sorted_bm25_sigma)
##        self.writeFile("lmlaplace", query_num, sorted_lm_laplace)
        self.writeFile("lmjm", query_num, sorted_lm_jm)

    def okapiTF(self, tf, doc_len):
        okapi_tf = tf / (tf + 0.5 + 1.5 * (doc_len/self.avgd))
        return okapi_tf

    def tfiDF(self, okapi_tf, df):
        tf_idf = okapi_tf * (math.log(self.count) - math.log(df))
        return tf_idf

    def okapiBM25(self, tf, doc_len, df):
        k1 = 1.5
        k2 = 1.5
        b = 0.75
        part1 = (math.log(self.count + 0.5) - math.log(df + 0.5))
        part2 = (tf + k1 * tf) / (tf + k1 * ((1-b) + b * (doc_len/self.avgd)))
        bm25 = part1 * part2
        return bm25

    def lm_laplace(self, tf, doc_len):
        p_laplace = (tf + 1.0)/(doc_len + self.vsize)
        return math.log(p_laplace)

    def lm_jm(self, tf, doc_len, sum_tf, sum_len, lam):
        p_jm = lam * (tf/doc_len) + (1-lam) * (sum_tf/self.vsize)
        return math.log(p_jm)
        

    def writeFile(self,filename,query_num,query_result):
        """
        Write the result in given name file
        :param filename: the output filename
        :param query_num: query number
        :param query_result: a dictionary stores the query reuslt
        """
        output = self.outputPath + filename
        if not os.path.exists(output):
            f=open(output, "w")
        else :
            f=open(output, "a")
        count = 1
        for k in query_result:
            if count <= 1000:
                f.write('%s Q0 %s %d %f Exp\n'%(query_num, k[0], count, k[1]))
                count += 1
            else: break
        f.close()
