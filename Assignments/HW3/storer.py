from elasticsearch import Elasticsearch
import os
path = '/Users/xinshu/desktop/CS6200/Assignments/HW3/data/'

class Store:

    def __init__(self):
        self.client = Elasticsearch()
        self.index = 'crawler_beauty'
        self.doc_type = 'document'
        self.url_dic = []

    def insert(self, count, url, header, title, text,
               raw, in_links, out_links, level):
        
##        if not self.search_url(url):           
        try:
            body = {
                'docno': str(count),
                'url': url,
                'HTTPheader': header,
                'title': title,
                'text': text,
                'html_Source': raw,
                'in_links': [],
                'out_links': out_links,
                'author': 'xshu',
                'depth': level
            }
                
##            self.client.index(index = self.index, doc_type = self.doc_type,
##                              id = url, body = body)
            self.client.index(index = 'crawler_beauty1', doc_type = self.doc_type,
                              id = url, body = body)
            self.url_dic.append(url)
            
        except Exception as e:
            print 'ES insert exception: {}'.format(e)

    def write_urls(self):
        output = path + 'urls'
        fh = open(output, "w")

        for url in self.url_dic:
            fh.write('%s\n'%(url))
            
        fh.close()


    def search_url(self, url):
        body={
              "query": {
                 "match": {
                   "_id": url
                 }
              }
            }
        
        res = self.client.search(index=self.index, doc_type=self.doc_type, body=body)          
     
        if res['hits']['total'] > 0:
            return True
        else:
            return False
                
