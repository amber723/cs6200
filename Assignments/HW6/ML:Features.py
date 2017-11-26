import random, operator
from sklearn import linear_model, svm, tree
import warnings
warnings.filterwarnings(action="ignore", module="scipy",
                        message="^internal gelsd")

from elasticsearch import Elasticsearch
es = Elasticsearch()
INDEX = 'ap_dataset'
DOC_TYPE = 'document'

FILE_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW1/results/'
QREL_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW1/qrels.adhoc.51-100.AP89.txt'
QUERY_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW1/query_desc.51-100.short.txt'
RESULT_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW6/performance/'

QUERY_LIST = []
TRAIN_QUERY = []
TEST_QUERY = []

MIN_VAL = -500
FEATURE_LIST = ['tfidf', 'okapitf', 'bm25', 'lmjm', 'lmlaplace']

MIN_SCORE = {'tfidf': 0, 'okapitf': 0, 'bm25': 0, 'lmjm': MIN_VAL,
             'lmlaplace': MIN_VAL}

label_map = {}
feature_map = {}

train_feature_matrix = []
test_feature_matrix = []
train_label_vector = []
test_label_vector = []
train_index = []
test_index = []
    
################################################################################
########                      BUILDING MATRICS                          ########                   
################################################################################

def get_doc_lst():
    doc_lst = []
    body={
        "query": {
            "match_all": {}
        }
    }       
    doc = es.search(index= INDEX, doc_type = DOC_TYPE,
                             body = body, explain = False,
                             scroll = "100m", size = 100)

    while len(doc['hits']['hits']) > 0:
        scrollId = doc['_scroll_id']
    
        for i in doc['hits']['hits']:
            doc_no = i['_source']['docno']
            doc_lst.append(doc_no)

        doc = es.scroll(scroll_id = scrollId, scroll = '1000ms')

    return doc_lst

def get_query_list():
    fh = open(QUERY_PATH, "r")    
    for line in fh.readlines():
        query_id = line.split(".")[0]
        if query_id not in QUERY_LIST:
            QUERY_LIST.append(query_id)

    print "The query list length is:", len(QUERY_LIST)
    random_split_set()
    fh.close()

def random_split_set():
    global TRAIN_QUERY
    global TEST_QUERY
    TRAIN_QUERY = random.sample(QUERY_LIST, 20)
    TEST_QUERY = list(set(QUERY_LIST) - set(TRAIN_QUERY))

def read_qrel_to_map():
    doc_lst = get_doc_lst()
    print 'doc_lst length: ', len(doc_lst)
    count = 1
    last_id = 0
    fh = open(QREL_PATH, "r")
    for line in fh.readlines():
        query_id, _, doc_id, grade = line.split()
        if query_id in QUERY_LIST:
            label_map[(query_id, doc_id)] = int(grade)
            if query_id == last_id:
                count +=1
            elif last_id == 0:
                last_id = query_id
            else:
                print count
                add_to_1000_docs(last_id, doc_lst, count)
                last_id = query_id
                count = 1
            
    print "The label map length is:", len(label_map)
    fh.close()

def add_to_1000_docs(query_id, doc_lst, count):
    for doc_id in doc_lst:
        if (query_id, doc_id) not in label_map:
            label_map[(query_id, doc_id)] = 0
            count += 1
        if count >= 1000:
            break

def read_file_to_map():
    for feature in FEATURE_LIST:
        print "Process feature:", feature
        path = FILE_PATH + feature
        fh = open(path, "r")
        
        for line in fh.readlines():
            query_id, _, doc_id, _, score, _ = line.split()
            score = float(score)
            
            if (query_id, doc_id) in label_map:
                if (query_id, doc_id) not in feature_map:
                    feature_map[(query_id, doc_id)] = {feature:score}
                else:
                    feature_map[(query_id,doc_id)][feature] = score
                    
        fh.close()
        
    print "The feature map leangth is:", len(feature_map), '\n'

def build_feature_label_matrix():
    for pairs in sorted(label_map.keys()):
        query_id = pairs[0]
        
        if pairs in feature_map:
            tmp_feature = feature_map[pairs]
        else:
            tmp_feature = {}
            
        grade = label_map[pairs]
        feature_vector = []
        
        for feature in FEATURE_LIST:
            if feature in tmp_feature:
                feature_vector.append(tmp_feature[feature])
            else:
                feature_vector.append(MIN_SCORE[feature])

        if query_id in TRAIN_QUERY:
            train_index.append(pairs)
            train_feature_matrix.append(feature_vector)
            train_label_vector.append(grade)
            
        elif query_id in TEST_QUERY:
            test_index.append(pairs)
            test_feature_matrix.append(feature_vector)
            test_label_vector.append(grade)
        

################################################################################
########                          TRAINING                              ########                   
################################################################################

def run_machinelearning_model():
    linear_regression()
    decision_tree()
    support_vector_machine()

def linear_regression():
    clf = linear_model.LinearRegression()
    clf.fit(train_feature_matrix, train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result,
                                                       test_result)
        
    write_to_file(train_result_map, "linear_regression_train_performance")
    write_to_file(test_result_map, "linear_regression_test_performance")

def decision_tree():
    clf = tree.DecisionTreeClassifier()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result,
                                                       test_result)

    write_to_file(train_result_map, "decision_tree_train_performance")
    write_to_file(test_result_map, "decision_tree_test_performance")

def support_vector_machine():
    clf = svm.SVC()
    clf.fit(train_feature_matrix,train_label_vector)
    train_result = clf.predict(train_feature_matrix)
    test_result = clf.predict(test_feature_matrix)
    train_result_map, test_result_map = analyse_result(train_result,
                                                       test_result)

    write_to_file(train_result_map, "svm_train_performance")
    write_to_file(test_result_map, "svm_test_performance")

def analyse_result(raw_train_result, raw_test_result):
    train_result = {}
    test_result = {}
    
    for i in range(len(raw_train_result)):
        pairs = train_index[i]
        query_id = pairs[0]
        doc_id = pairs[1]
        score = raw_train_result[i]
        
        if query_id not in train_result:
            train_result[query_id] = {doc_id: score}
        else:
            train_result[query_id][doc_id] = score
            
    for i in range(len(raw_test_result)):
        pairs = test_index[i]
        query_id = pairs[0]
        doc_id = pairs[1]
        score = raw_test_result[i]
        
        if query_id not in test_result:
            test_result[query_id] = {doc_id: score}
        else:
            test_result[query_id][doc_id] = score

    return train_result, test_result

def write_to_file(result_map, filename):
    outpath = RESULT_PATH + filename
    fh = open(outpath, "w")
    
    for query_id in result_map:
        result = result_map[query_id]
        sorted_result = sorted(result.items(), key=operator.itemgetter(1),
                               reverse = True)
        count = 1
        for element in sorted_result:
            if count <= 1000:
                fh.write('%s Q0 %s %d %f Exp\n'%(query_id, element[0],
                                                 count, element[1]))
                count+= 1
            else:
                break
    fh.close()


################################################################################
########                        MAIN FUNCTION                           ########                   
################################################################################

def main():
    get_query_list()
    print "The train query list is:", TRAIN_QUERY
    print "The test query list is:", TEST_QUERY, '\n'
    
    read_qrel_to_map()
    read_file_to_map()
    build_feature_label_matrix()
    
    print "The train feature matrix length is:", len(train_feature_matrix)
    print "The train label length is:", len(train_label_vector)
    print "The train index length is:", len(train_index)
    
    print "The test feature matrix length is:", len(test_feature_matrix)
    print "The test label length is:", len(test_label_vector)
    print "The test index length is:", len(test_index)
    
    run_machinelearning_model()


if __name__=='__main__':
    main()
