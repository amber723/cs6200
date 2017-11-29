from elasticsearch import Elasticsearch
from sklearn import tree
import string, operator

es = Elasticsearch()

LABEL_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/trec07p/full/index'
RESULT_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/result'
ngrams_list = ['free', 'win', 'porn', 'join', 'deal', 'earn', 'order',
               'viagra', 'buy', 'clearance', 'subscribe', 'click', 'valium']
INDEX = 'spam'
DOC_TYPE = 'document'

train_label_vector = []
test_label_vector = []
train_feature_matrix = []
test_feature_matrix = []
train_set = set()
test_set = set()
train_index = []
test_index = []
label_map = {}
feature_map = {}
train_result = {}
test_result = {}

def read_label_to_map():
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

def build_feature_map():
    for gram in ngrams_list:
        body={
          "_source": "class",
          "query": {
             "match": {
               "text": gram
             }
          },
          "script_fields": {
            "tf":{
              "script":{
                "lang": "groovy",
                "inline": "_index['text'][term].tf()",
                "params": {
                  "term": gram
                }
              }
            }
          }
        }

        resp = es.search(index=INDEX, doc_type=DOC_TYPE, body=body,
                         explain=False, scroll="100m", size=100)
        
        total_number = resp['hits']['total']
        print gram, ' : ', total_number
        
        while len(resp['hits']['hits']) > 0:
            scrollId= resp['_scroll_id']

            for i in resp['hits']['hits']:
                tf = i['_score']
                doc_id = i['_id']
                class_set = i['_source']['class']
                
                if class_set == 'train':
                    train_set.add(doc_id)
                else:
                    test_set.add(doc_id)
                    
                if doc_id not in feature_map:
                    feature_map[doc_id] = {gram: tf}
                else:
                    feature_map[doc_id][gram] = tf
                    
            resp = es.scroll(scroll_id = scrollId, scroll='1000ms')


def build_feature_matrix():
    train_matrix_path = RESULT_PATH + '/manual_train_feature_matrix'
    test_matrix_path = RESULT_PATH + '/manual_test_feature_matrix'
    train_fh = open(train_matrix_path, "w")
    test_fh = open(test_matrix_path, "w")
    
    for doc_id in feature_map:
        map = feature_map[doc_id]
        label = label_map[doc_id]
        vector = []
        
        for word in ngrams_list:
            if word in map:
                vector.append(map[word])
            else:
                vector.append(0)
        
        if doc_id in train_set:
            train_index.append(doc_id)
            train_feature_matrix.append(vector)
            train_label_vector.append(label)
            write_vector_to_file(label, map, train_fh)
        elif doc_id in test_set:
            test_index.append(doc_id)
            test_feature_matrix.append(vector)
            test_label_vector.append(label)
            write_vector_to_file(label, map, test_fh)

    train_fh.close()
    test_fh.close() 
    print "\nThe train feature matrix length is:", len(train_feature_matrix)
    print "The test feature matrix length is:", len(test_feature_matrix), '\n'

def write_vector_to_file(label, feature_matrix, fh):
    fh.write('%d'%label)
    if feature_matrix:
        for index in sorted(feature_matrix.keys()):
            fh.write(' %s:%s'%(index, feature_matrix[index]))
    fh.write('\n')

def decision_tree_model():
    print 'Training with decision tree...'
    clf = tree.DecisionTreeClassifier()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result,
                                                       test_result)
    write_to_file(train_result_map, "decision_tree_train_performance")
    write_to_file(test_result_map, "decision_tree_test_performance")

def analyse_result(raw_train_result, raw_test_result):
    print 'Analysing results...'
    train_result = {}
    test_result = {}
    train_accuracy = 0
    test_accuracy = 0
    
    for i in range(len(raw_train_result)):
        doc_id = train_index[i]
        score = raw_train_result[i]
        train_result[doc_id] = score
        if int(score) == int(label_map[doc_id]):
            train_accuracy += 1
    train_acc = float(train_accuracy) / len(train_index)
    
    for i in range(len(raw_test_result)):
        doc_id = test_index[i]
        score = raw_test_result[i]
        test_result[doc_id] = score
        if int(score) == int(label_map[doc_id]):
            test_accuracy += 1
    test_acc = float(test_accuracy) / len(test_index)
    
    print "The train correct number is:", train_accuracy
    print "The test correct number is:", test_accuracy
    print "The train set accuracy is:", train_acc
    print "The test set accuracy is:", test_acc, '\n'

    return train_result, test_result

def write_to_file(result_map, filename):
    outpath = RESULT_PATH + '/' + filename
    fh = open(outpath, "w")
    sorted_result = sorted(result_map.items(), key=operator.itemgetter(1),
                           reverse = True)
    count = 1
    accuracy = 0
    for pair in sorted_result:
        fh.write('%s %d %f Exp\n'%(pair[0], count, pair[1]))
        if count <= 50:
            if int(pair[1]) == int(label_map[pair[0]]):
                accuracy += 1
        count += 1

    print 'Top 50 spam accuracy for', filename, 'is: ', float(accuracy) / 50
    fh.close()

def main():
    read_label_to_map()
    build_feature_map()
    build_feature_matrix()
    decision_tree_model()

if __name__ == '__main__':
    main()
