import string, hashlib

# QUERY_LIST = ['152101', '152102', '152103']
EVAL = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/eval_docs_merged.txt'
QREL = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/qrel.txt'
RANK = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/rank.txt'

def read_eval():
    fh = open(EVAL, "r")
    qrel = open(QREL, "w")
    rank = open(RANK, "w")
    
    last_query_id = ''
    count = 1
    for line in fh.readlines():
        line = string.strip(line, "\n")
        query_id, url, grade = line.split(' ')
        if query_id == last_query_id:
            count += 1
        else:
            count = 1
        last_query_id = query_id
        
        print query_id, url, grade
        hash_url = hashlib.md5(url).hexdigest()
        qrel.write('%s %s %s %s\n'%(query_id, 'merged', hash_url, grade))
        rank.write('%s %s %s %d %s %s\n'%(query_id, 'Q0', hash_url, count, 'score', 'Exp'))

    fh.close()
    qrel.close()
    rank.close()

def main():
    read_eval()


if __name__ == '__main__':
    main()

