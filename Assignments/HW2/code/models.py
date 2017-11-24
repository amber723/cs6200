#!/user/bin/python
from __future__ import division
import os, sys, math, operator, heapq

OUTPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW2/models/'
DOCLEN_FILE = '/Users/xinshu/desktop/CS6200/Assignments/HW2/doc_len'
DOCID_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW2/doc_id'
RESULT = '/Users/xinshu/desktop/CS6200/Assignments/HW2/result/'

class QueryModel:
    """
    This class calculate IR models
    """
    def __init__(self):
        self.docIdDict = self.getDocId()
        self.vsize, self.catalog = self.getVsize()
        self.count, self.avgd, self.doc_len_dict = self.getDocLenDict()
        self.outputPath = OUTPATH

        print "The total document numbers is: " + str(self.count)
        print "The average length of documents is: " + str(self.avgd)
        print "The vocabulary size is: " + str(self.vsize)

    def getDocId(self):
        """
        read the doc id file and build a map for id and real doc id,
        """
        fh = open(DOCID_PATH, "r")
        doc_id_dict = {}
        for l in fh.readlines():
            id = l.split(" ")[0]
            doc_id = l.split(" ")[1][:-1]
            doc_id_dict[id] = doc_id
        fh.close()
        return doc_id_dict

    def getDocLenDict(self):
        doc_len_dict = {}
        total_len = 0
        fh = open(DOCLEN_FILE, "r")
        
        for l in fh.readlines():
            doc_id = l.split(" ")[0]
##            doc_id = self.docIdDict[id]
            doc_len = int(l.split(" ")[1][:-1])
            doc_len_dict[doc_id] = doc_len
            total_len += doc_len
            
        dcount = len(doc_len_dict)
        avglen = float(total_len) / float(dcount)
        return dcount, avglen, doc_len_dict

    def getVsize(self):
        filename = RESULT + "catalog"
        fh = open(filename, "r")
        catalog = {}
        
        for l in fh.readlines():
            term = l.split(" ")[0]
            start = l.split(" ")[1]
            length = l.split(" ")[2][:-1]
            catalog[term] = [start, length]
            
        return len(catalog), catalog

    def getCataList(self, term):
        start = int(self.catalog[term][0])
        length = int(self.catalog[term][1])
        
        filename = RESULT + "index"
        fh = open(filename, "r")
        fh.seek(start)
        term_index = fh.read(length)[:-1].split(" ")
        fh.close()
        return term_index
    
    def getTF(self, term):
        tf = {}
        pos_dict = {}
        df = 0
        sum_doclen = 0
        sum_tf = 0
        
        if term not in self.catalog:
            return df, tf, sum_doclen, sum_tf, pos_dict

        term_index = self.getCataList(term)
        
        for i in range(len(term_index)):
            if i % 3 == 0: #doc_id
                id = term_index[i]
                doc_id = self.docIdDict[id]
                df += 1
            elif i % 3 == 1: #tf
                doc_tf = int(term_index[i])
                tf[doc_id] = doc_tf
                sum_tf += doc_tf
            else: #pos_lst
                pos_lst = map(int, term_index[i].split(","))
                pos_dict[doc_id] = pos_lst
                
            sum_doclen += self.doc_len_dict[doc_id]

        for doc_id in self.docIdDict.itervalues():
            if doc_id not in tf:
                tf[doc_id] = 0
            
        return df, tf, sum_doclen, sum_tf, pos_dict
        
    def models(self, query_num, query):
        """
        given a query and calculate the score using five models,
        which are okapiTF, TFiDF, okapiBM25, LM_laplace and LM_jm.
        write the first 1000 result to the file
        :param query_num: the query num
        :param query: a dictionary contains word and its frequency
        """
        okapi_tf_sigma = {}
        tf_idf_sigma = {}
        bm25_sigma = {}
        lm_laplace = {}
        lm_jm = {}       
        query_len = len(query)

        for word in query:
            df, tfs, sumlen, sumtf, _ = self.getTF(word)
            if df ==0:
                continue
            for doc_no, tf in tfs.iteritems():
                doc_len = self.doc_len_dict[doc_no]
                if doc_len == 0:
                    print ('doclen = 0', doc_no)
                    continue
                okapi_tf = self.okapiTF(tf, doc_len)
                tf_idf = self.tfiDF(okapi_tf, df)
                bm25 = self.okapiBM25(tf, doc_len, df)
                log_p_laplace = self.lm_laplace(tf, doc_len)
                log_p_jm = self.lm_jm(tf, doc_len, sumtf, sumlen)
                
                if doc_no in okapi_tf_sigma:
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

        self.writeFile("okapitf", query_num, okapi_tf_sigma)
        self.writeFile("tfidf", query_num, tf_idf_sigma)
        self.writeFile("bm25", query_num, bm25_sigma)
        self.writeFile("lmlaplace", query_num, lm_laplace)
        self.writeFile("lmjm", query_num, lm_jm)

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

    def lm_jm(self, tf, doc_len, sum_tf, sum_len):
        lam = 0.99
        p_jm = lam * (tf/doc_len) + (1- lam)*(sum_tf/self.vsize)
        if p_jm == 0:
            print (tf, doc_len, sum_tf, self.vsize)
        return math.log(p_jm)

    def writeFile(self,filename,query_num,query_result):
        """
        Write the result in given name file
        :param filename: the output filename
        :param query_num: query number
        :param query_result: a dictionary stores the query reuslt
        """
        sorted_query_result = sorted(query_result.items(), key=operator.itemgetter(1), reverse = True)
        output = self.outputPath + filename
        if not os.path.exists(output):
            f=open(output, "w")
        else :
            f=open(output, "a")
        count = 1
        for k in sorted_query_result:
            if count > 1000:
                break
            f.write('%s Q0 %s %d %f Exp\n'%(query_num, k[0], count, k[1]))
            count += 1
        f.close()

    def proximity_model(self, num, query):
        doc_term_pos_dict = {}
        for word in query:
            print word
            _, _, _, _, pos_dict = self.getTF(word)
            
            for id in pos_dict.keys():
                if id in doc_term_pos_dict:
                    doc_term_pos_dict[id].append({word: pos_dict[id]})
                else:
                    doc_term_pos_dict[id] = [{word: pos_dict[id]}]
            
        doc_score_dict = {}
        for id, lst in doc_term_pos_dict.iteritems():
            if len(lst) == 1: #only one query word occurs in this doc
                score = 0
            else:
                score = self.getProximityScore(id, lst)
            doc_score_dict[id] = score
##            print (id, score)

        print num
        self.writeFile("proximity", num, doc_score_dict)

    def getProximityScore(self, id, term_pos_list):
##        print (id, term_pos_list)
        c = 1500
        doc_len = self.doc_len_dict[id]
        min_span = doc_len
        num_word = len(term_pos_list)
        hp = []
        
        for i in range(len(term_pos_list)):
            word = term_pos_list[i].keys()[0]
            pos = term_pos_list[i][word][0]
            heapq.heappush(hp, (pos, i, 0))
        
            
        while len(hp)>= num_word:
            largest = heapq.nlargest(1, hp)[0][0]
            smallest = heapq.nsmallest(1, hp)[0][0]
            span = largest - smallest
            
            if span < min_span:
                min_span = span
                
            tmp_tuple = heapq.heappop(hp)
##            print (tmp_tuple, min_span)
            i = tmp_tuple[1]
            word = term_pos_list[i].keys()[0]
            next_list_pos = tmp_tuple[2] + 1
            
            if next_list_pos >= len(term_pos_list[i][word]):
                continue
            else:
                pos = term_pos_list[i][word][next_list_pos]
                heapq.heappush(hp, (pos, i, next_list_pos))
                
        score = float((c - min_span) * num_word) / (doc_len + self.vsize)
        return score
