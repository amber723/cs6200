from elasticsearch import Elasticsearch
import os
path = '/Users/xinshu/desktop/CS6200/Assignments/HW3/data/'

class Store:

    def __init__(self):
        self.client = Elasticsearch()
        self.index = 'test'
        self.doc_type = 'document'

    def insert(self, count, url, header, title, text,
               raw, in_links, out_links, level):
        
        if not self.search_url(url):           
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
                    
                self.client.index(index = self.index, doc_type = self.doc_type,
                                  id = url, body = body)
                
            except Exception as e:
                print 'ES insert exception: {}'.format(e)


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
                

def read_files():
    filenamelist = os.listdir(path)
    
    for x in xrange(len(filenamelist)):
            filename = path+"/"+filenamelist[x]
            parse_file(filename)


def parse_file(fn):
    fh = open(fn, "r")
    l = fh.readline()
    
    while l:
        while l and '<DOC>' not in l:
            l = fh.readline()
            
        while l and '<DOCNO>' not in l:
            l = fh.readline()
        docno = l.lstrip('<DOCNO>').rstrip('</DOCNO>\n')

        while l and '<URL>' not in l:
            l = fh.readline()
        url = l.lstrip('<URL>').rstrip('</URL>\n')

        while l and '<DEPTH>' not in l:
            l = fh.readline()
        depth = l.lstrip('<DEPTH>').rstrip('</DEPTH>\n')

        while l and '<HEAD>' not in l:
            l=fh.readline()
        title =l.lstrip('<HEAD>').rstrip('</HEAD>\n')

        while l and '<HTTPHEADER>' not in l:
            l=fh.readline()
        HTTPheader = ''
        if l and '<HTTPHEADER>' in l:
            l=fh.readline()
            while l and '</HTTPHEADER>' not in l:
                    HTTPheader += l
                    l =fh.readline()

        while l and '<OUT_LINKS>' not in l:
            l=fh.readline()
        out_links = []
        if l and '<OUT_LINKS>' in l:
            l=fh.readline()
            while l and '</OUT_LINKS>' not in l:
                    out_links.append(l[:-1])
                    l =fh.readline()

        while l and '<TEXT>' not in l:
            l=fh.readline()
        text = ''
        if l and '<TEXT>' in l:
            l=fh.readline()
            while l and '</TEXT>' not in l:
                    text += l
                    l =fh.readline()

        while l and '<HTML>' not in l:
            l=fh.readline()
        html_Source = ''
        if l and '<HTML>' in l:
            l=fh.readline()
            while l and '</HTML>' not in l:
                    html_Source += l
                    l =fh.readline()

        
        store.insert(docno, url, HTTPheader, title, text,
           html_Source, [], out_links, depth)

    fh.close()

store = Store()
read_files()
