import string, timeit
from elasticsearch import Elasticsearch

es = Elasticsearch()
myindex = 'crawler_beauty1'
mydoc_type = 'document'

def write_to_file():

    out_put_path = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/link_file.txt'
    out_file = open(out_put_path, 'w')
    try:
        body = {
            "_source": ['out_links', 'in_links', 'url'],
            "query": {
                "match_all": {}
            }
        }

        resp = es.search(index = myindex, doc_type= mydoc_type, body=body,
                         scroll='1000m', size=500)
    except Exception as e:
        print 'ES search exception: {}'.format(e)

    
    while len(resp['hits']['hits']) > 0:
        scroll_id = resp['_scroll_id']
        print 'scrolling...'
        
        for i in resp['hits']['hits']:
            url = string.strip(i['_source']['url'])
            out_size = 0
            ins = []
            if 'out_links' in i['_source']:
                out_size = len(i['_source']['out_links'])
            if 'in_links' in i['_source']:
                for in_link in i['_source']['in_links']:
                    in_link = in_link.encode('ascii','ignore')
                    ins.append(string.strip(in_link))
            out_file.write('{}\t{}\t{}\n'.format(url.encode('ascii','ignore'), out_size, '\t'.join(ins)))

        resp = es.scroll(scroll_id=scroll_id, scroll='1000m')

    out_file.close()


if __name__ == '__main__':
    start = timeit.default_timer()
    
    write_to_file()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60))
    
