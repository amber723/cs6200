import string, timeit
from elasticsearch import Elasticsearch

es = Elasticsearch()
myindex = 'crawler_beauty1'
mydoc_type = 'document'

def write_to_file():

    out_put_path = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/top1000.urls.txt'
    out_file = open(out_put_path, 'w')
    try:
        body = {
            "_source": 'url',
            "query": {
                "match_all": {}
            }
        }

        resp = es.search(index = myindex, doc_type= mydoc_type,
                         body=body, size=1000)
    except Exception as e:
        print 'ES search exception: {}'.format(e)

        
    for i in resp['hits']['hits']:
        url = string.strip(i['_source']['url'])
        out_file.write('{}\n'.format(url.encode('ascii','ignore')))

    out_file.close()


if __name__ == '__main__':
    start = timeit.default_timer()
    
    write_to_file()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60))
    
