from elasticsearch import Elasticsearch
import os, json, timeit, json

path = '/Users/xinshu/desktop/CS6200/DATA/AP_DATA/ap89_collection'
INDEX = 'ap_dataset'
DOC_TYPE = 'document'

es=Elasticsearch()

def main():
        start = timeit.default_timer()
        
        read_files()
        
        stop = timeit.default_timer()
        print ('run time', stop - start)
        
def read_files():
        filenamelist=os.listdir(path)
        id = 0
        
        for x in xrange(len(filenamelist)):
                filename = path+"/"+filenamelist[x]
                id = parse_file(filename, id)
                print('indexing: '+ filename, 'id: '+ str(id))
                 
        print id
        
##        test = es.get(index= INDEX, doc_type = DOC_TYPE, id = 5)
##        print json.dumps(test, indent = 4)

def parse_file(fn, id):
        fh = open(fn, "r")
        l = fh.readline()
        while l:
                while l and '<DOC>' not in l:
                        l=fh.readline()
                while l and '<DOCNO>' not in l:
                        l=fh.readline()
                doc_id=l.split(" ")[1]
                while l and '<TEXT>' not in l:
                        l=fh.readline()
                text=''
                while l and '<TEXT>' in l:
                        l=fh.readline()
                        while l and '</TEXT>' not in l:
                                text += l
                                l =fh.readline()
                        while l and '<TEXT>' not in l and '<DOC>' not in l:
                                l =fh.readline()
                        if l and '<TEXT>' in l:
                                continue
                        else: break
                        
                es.index(index = INDEX, doc_type = DOC_TYPE, id = id,
                        body={"docno": doc_id, "text": text,
                              "doc_l": len(text.split())})
                id += 1

        fh.close()
        return id

if __name__ == '__main__':
	main()
