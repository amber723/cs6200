import string

EVAL1 = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/eval_docs_xshu.txt'
EVAL2 = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/eval_docs_wqin.txt'
EVAL3 = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/eval_docs_hgao.txt'
RESULT = '/Users/xinshu/desktop/CS6200/Assignments/HW5/data/eval_docs_merged.txt'

def merge_results():
    eval1 = open(EVAL1, "r")
    eval2 = open(EVAL2, "r")
    eval3 = open(EVAL3, "r")
    result = open(RESULT, "w")

    for l in eval1.readlines():
        l2 = eval2.readline()
        l3 = eval3.readline()
        
        l = string.strip(l, "\n")
        query_id, url, grade = l.split(' ')

        grade = int(grade)
        grade2 = int(string.strip(l2, "\n")[-1])
        grade3 = int(string.strip(l3, "\n")[-1])

        avg_grade = float(grade + grade2 + grade3)/3
        avg_grade = int(round(avg_grade))

        result.write('%s %s %s\n'%(query_id, url, avg_grade))

    eval1.close()
    eval2.close()
    eval3.close()
    result.close()

def main():
    merge_results()

if __name__ == '__main__':
    main()
