from elasticsearch import Elasticsearch
import timeit

PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW3/data/'
client = Elasticsearch()
index = 'crawler_beauty1'
doc_type = 'document'

def insert(url, lst):
    if search_url(url):
        try:
            body = {
                "query": {
                    "script":{
                        "inline": "ctx._source.in_links.addAll(params.new_inlinks)",
                        "lang": "painless",
                        "params": {"new_inlinks": lst}
                    }
                }
            }
                
            client.update(index = index, doc_type = doc_type,
                              id = url, body = body)
            
        except Exception as e:
            print 'ES insert exception: {}'.format(e)

def search_url(url):
    body={
          "query": {
             "match": {
               "_id": url
             }
          }
        }
    
    res = client.search(index=index, doc_type=doc_type, body=body)          
 
    if res['hits']['total'] > 0:
        return True
    else:
        return False

def read_inlink_file():
    filename = PATH + 'in_links'
    fh = open(filename, "r")
    l = fh.readline()
    count = 0
    while l and '<url>' in l:
        url = l[5:-7]
        count += 1
        l = fh.readline()[:-1]
        if l and '<in_links>' in l:
            lst = l[10:-11].split(" ")
            insert(url, lst)
            l=fh.readline()

    print count
    print url
    fh.close()

def main():
        start = timeit.default_timer()
        
        read_inlink_file()
        
        stop = timeit.default_timer()
        print ('run time', int(stop - start))
        
if __name__ == '__main__':
	main()
    
