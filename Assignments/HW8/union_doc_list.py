from collections import defaultdict, OrderedDict

BM25_PATH = "/Users/xinshu/desktop/CS6200/Assignments/HW1/results/bm25"
QREL_PATH = "/Users/xinshu/desktop/CS6200/Assignments/HW1/qrels.adhoc.51-100.AP89.txt"
DATA_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW8/data/doc_list'

def read_qres():
    qrel = defaultdict(lambda: defaultdict(lambda: 0))

    for line in open(QREL_PATH):
        qid, _, docid, rel = line.split()
        rel = int(rel)
        qrel[qid][docid] = rel

    return qrel

def read_trec():
    trec = defaultdict(lambda: {})

    for line in open(BM25_PATH):
        qid, _, docid, _, score, _ = line.split()
        if len(trec[qid]) < 1000:
            trec[qid][docid] = float(score)

    trec = OrderedDict(sorted(trec.items()))
    return trec

def union_doc_list(trec, qres):
    doc_list = defaultdict(lambda: set())

    for qid in trec:
        for docid in trec[qid]:
            doc_list[qid].add(docid)

    for qid in qres:
        if qid in trec:
            for docid in qres[qid]:
                if qres[qid][docid] == 1:
                    doc_list[qid].add(docid)

    of = open(DATA_PATH, "w")
    for qid in doc_list:
        for docid in doc_list[qid]:
            of.write(qid + " " + docid + "\n")

if __name__ == "__main__":
    trec = read_trec()
    qres = read_qres()

    union_doc_list(trec, qres)
