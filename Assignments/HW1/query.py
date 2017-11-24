#!/user/bin/python
# This script get each query from elasticsearch and 
# pass the query to models class

from elasticsearch import Elasticsearch
import os, sys, timeit
import math
import models
import json

QUERYFILE='/Users/xinshu/desktop/CS6200/DATA/AP_DATA/query_desc.51-100.short.txt'
QUERYFILE_origin='/Users/xinshu/desktop/CS6200/DATA/AP_DATA/query_desc.51-100.short.original.txt'
INDEX = 'ap_dataset'
QUERY_TYPE = 'query'
DOC_TYPE = 'document'

es = Elasticsearch()

def main():
    start = timeit.default_timer()

    i = 0
    querys = getQuerys()
    m = models.QueryModel(es, INDEX, DOC_TYPE)

    for query_num, query in querys.iteritems():
            i += 1
            print (i, query_num)
            print query
            m.models(query, query_num)

    stop = timeit.default_timer()
    print ('finish search... run time: ', stop - start)


def getQuerys():
    fh=open(QUERYFILE,"r")
    fh_o=open(QUERYFILE_origin,"r")
    querys=fh.readlines()
    print querys
    querys_o=fh_o.readlines()
    new_querys = {}
    
    for i in range(0,len(querys)):
        query_map = {}
        query = querys[i]
        query_o = querys_o[i]
        no = query.split('.')[0]
        new_query = query[:len(query) - 1].split(" ")[1:]
        new_query_o = query_o[:len(query_o) - 1].split(" ")[1:]
        for j in range(0, len(new_query)):
            query_map[new_query[j]]=new_query_o[j]
        new_querys[no]=query_map
              
    fh.close()
    return new_querys


if __name__ == '__main__':
    main()
