from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch()
index = 'crawler_beauty'
doc_type = 'document'
cnt = 0
now = datetime.now()

def getScrollInfo(size = 1000):
    results =  es.search(
        index = index, doc_type = doc_type, size = size,
        scroll = '15m',
        body = {
            "_source": "url",
            "query":{
                    "match":{ "author": "xshu"} }
            }, request_timeout = 30)
    return results

def update(url):
    try:
        es.update(index = index, doc_type = doc_type, id = url,
          body = {
              "query":{
                    "script" : {
                        "inline": "ctx._source.depth -= 1",
                        "lang": "painless"}}})
    except Exception as e:
        print url, e
    return

def updateDepth(data, cnt):
    for doc in data:
        url = doc['_id']
        update(url)

        cnt += 1
        if cnt % 100 == 0:
            print cnt, 'urls'
    return cnt

scroll = getScrollInfo()
scroll_id = scroll['_scroll_id']
while True:
    if len(scroll['hits']['hits']) == 0:
        break
    else:
        cnt = updateDepth(scroll['hits']['hits'], cnt)
    scroll = es.scroll(scroll_id = scroll_id, scroll= "15m")
    scroll_id = scroll['_scroll_id']

print 'running time', datetime.now() - now
