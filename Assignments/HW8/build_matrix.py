from elasticsearch import Elasticsearch
import pickle

DATA_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW8/data/'
es = Elasticsearch()
INDEX = 'ap_dataset'
DOC_TYPE = 'document'

def es_get_term_vector(client, did):
    res = client.termvectors(index = INDEX, doc_type = DOC_TYPE, id = did,
                             body = {'term_statistics' : True})
    try:
        info = res["term_vectors"]["text"]["terms"]
        return info
    except:
        return []

def es_get_all_ids(client):
    doc_dict = {}
    body={
        "query": {
            "match_all": {}
        }
    }       
    doc = client.search(index= INDEX, doc_type = DOC_TYPE,
                             body = body, explain = False,
                             scroll = "100m", size = 100)

    while len(doc['hits']['hits']) > 0:
        scrollId = doc['_scroll_id']
    
        for i in doc['hits']['hits']:
            doc_no = i['_source']['docno']
            doc_id = i['_id']
            doc_dict[doc_id] = doc_no

        doc = client.scroll(scroll_id = scrollId, scroll = '1000ms')

    return doc_dict

def store_matrix():
    all_ids = es_get_all_ids(es)
    used_ids = []
    f_matrix = {}
    
    count = 0
    for did, doc_no in all_ids.iteritems():
        count += 1
        if count % 1000 == 0:
            print 'processing...', count
            
        text = []
        term_list = es_get_term_vector(es, did)

        for term in term_list:
            if term_list[term]["term_freq"] > 3:
                for i in xrange(term_list[term]["term_freq"]):
                    text.append(term)

        if len(text) > 0:
            f_matrix[doc_no] = ' '.join(text)
            used_ids.append(doc_no)

    pickle.dump(f_matrix, open(DATA_PATH + 'feature_matrix.pkl', "w"))
    pickle.dump(used_ids, open(DATA_PATH + 'all_ids.pkl', "w"))

if __name__ == "__main__":
    store_matrix()
