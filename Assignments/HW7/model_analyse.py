from liblinearutil import *
import string, pickle, operator

LABEL_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/trec07p/full/index'
RESULT_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW7/result'
model_path = RESULT_PATH + '/model'

dictionary = {}

def run_liblinear():
    train_path = RESULT_PATH + '/train_feature_matrix'
    test_path = RESULT_PATH + '/test_feature_matrix'
    
    y1, x1 = svm_read_problem(train_path)
    y2, x2 = svm_read_problem(test_path)
    m = train(y1, x1, '-s 0')
    save_model(model_path, m)
    
    p_label, p_acc, p_val = predict(y2, x2, m, '-b 1')
    print_top_50_accuracy('test',p_val)

    p_label, p_acc, p_val = predict(y1, x1, m, '-b 1')
    print_top_50_accuracy('train', p_val)

def analyse_model():
    model_fh = open(model_path, "r")
    parameter_begin = False
    parameter_map = {}
    index = 0

    for line in model_fh.readlines():
        new_line = string.strip(line, "\n")
        if new_line == "w":
            parameter_begin = True
            continue
        if parameter_begin == True:
            index += 1
            unigram = dictionary[index]
            parameter_map[unigram] = float(line)
    sorted_parameter_map = sorted(parameter_map.items(),
                                  key=operator.itemgetter(1), reverse=True)

    model_fh.close()
    
    outpath = RESULT_PATH + '/unigram_rank'
    rank_fh = open(outpath, "w")
    for pair in sorted_parameter_map:
        rank_fh.write('%s\t%f\n'%(pair[0],pair[1]))
    rank_fh.close()

def read_dictionary():
    global dictionary
    inpath = RESULT_PATH + '/dictionary.p'
    reverse_dictionary = pickle.load(open(inpath, "rb"))
    for key in reverse_dictionary:
        dictionary[reverse_dictionary[key]] = key

def print_top_50_accuracy(type, arr):
    top_50_docs = print_top_50_docs(type, arr)
    label_map = read_label_to_map()
    correct = 0
    for doc_id in top_50_docs.keys():
        if label_map[doc_id] == 1:
            correct += 1
    acc = float(correct) / len(top_50_docs)
    print correct, len(top_50_docs)
    print 'Top 50 docs Accuracy for', type, ': ', acc
        
def read_label_to_map():
    label_map = {}
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
        
    return label_map

def print_top_50_docs(type, arr):
    probs = get_top50_prob(arr)
    doc_ids = get_doc_ids(type)

    top_50_docs = {}
    for key, prob in probs.iteritems():
        doc_id = doc_ids[key]
        top_50_docs[doc_id] = prob

    return top_50_docs

def get_doc_ids(type):
    if type == 'test':
        path = RESULT_PATH + '/test_set'
    else:
        path = RESULT_PATH + '/train_set'
    fh = open(path, "r")

    doc_list = {}
    i = 1
    for l in fh.readlines():
        doc_id = string.strip(l, '\n')
        doc_list[i] = doc_id
        i += 1

    return doc_list

def get_top50_prob(arr):
    prob = {}
    i = 1
    for pair in arr:
        if pair[0] > 0.9999999999999:
            prob[i] = pair[0]
        i += 1
    return prob
    

def main():
    run_liblinear()
##    read_dictionary()
##    analyse_model()

if __name__ == '__main__':
    main()
