from elasticsearch import Elasticsearch
import string, pickle, operator

LABEL_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/trec07p/full/index'
RESULT_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/result'
INDEX = 'spam'
DOC_TYPE = 'document'
es = Elasticsearch()

label_map = {}
dictionary = {}
index = 0
train_set = []
test_set = []

def read_label_to_map():
    print 'reading label...'
    fh = open(LABEL_PATH, "r")
    for line in fh.readlines():
        new_line = string.strip(line, '\n')
        [label, path] = new_line.split(' ')
        doc_id = path.split('/')[-1]

        if label == 'spam':
            grade = 1
        else:
            grade = 0
        label_map[doc_id] = grade

def read_train_test_set():
    print 'reading TRAIN and TEST sets...'
    train_path = RESULT_PATH + '/train_set'
    test_path = RESULT_PATH + '/test_set'
    
    train_fh = open(train_path, "r")
    for line in train_fh.readlines():
        doc_id = string.strip(line, '\n')
        train_set.append(doc_id)
    train_fh.close()
    
    test_fh = open(test_path, "r")
    for line in test_fh.readlines():
        doc_id = string.strip(line, '\n')
        test_set.append(doc_id)
    test_fh.close()

def write_feature_matrix():
    print 'writing feature matrix for TRAIN and TEST sets...'
    train_matrix_path = RESULT_PATH + '/train_feature_matrix'
    test_matrix_path = RESULT_PATH + '/test_feature_matrix'
    train_fh = open(train_matrix_path, "w")
    test_fh = open(test_matrix_path, "w")
    count = 0
    
    for doc_id in sorted(label_map.keys()):
        feature_map = query_doc(doc_id)
        label = label_map[doc_id]
        
        if doc_id in train_set:
            write_vector_to_file(label, feature_map, train_fh)
        elif doc_id in test_set:
            write_vector_to_file(label, feature_map, test_fh)
        count += 1
        
    train_fh.close()
    test_fh.close()

    print "The total size is:", count

def query_doc(doc_id):
    global index
    resp = es.termvectors(index=INDEX, doc_type=DOC_TYPE, id=doc_id)
    term_map = {}
    try:
        terms = resp['term_vectors']['text']['terms']
    except:
        return term_map
    
    for word in terms:
        tf = terms[word]['term_freq']

        if word not in dictionary:
            index += 1
            dictionary[word] = index
            term_map[index] = tf
        else:
            word_index = dictionary[word]
            term_map[word_index] = tf

    return term_map

def write_vector_to_file(label, feature_matrix, fh):
    fh.write('%d'%label)
    if feature_matrix:
        for index in sorted(feature_matrix.keys()):
            fh.write(' %d:%d'%(index, feature_matrix[index]))
    fh.write('\n')

def write_dictionary_file():
    outpath = RESULT_PATH + '/' + 'dictionary'
    fh = open(outpath, "w")
    sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1))
    for pair in sorted_dictionary:
        fh.write('%s\t%d'%(pair[0], pair[1]))
        
    outpath = RESULT_PATH + '/' + 'dictionary.p'
    pickle.dump(dictionary, open(outpath, "wb"))

def main():
    read_label_to_map()
    read_train_test_set()
    write_feature_matrix()
    write_dictionary_file()

if __name__ == '__main__':
    main()
