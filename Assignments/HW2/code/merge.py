#! user/bin/python

import heapq, os, gzip,timeit
CATALOG = '/Users/xinshu/desktop/CS6200/Assignments/HW2/catalog/'
TEMPINDEX = '/Users/xinshu/desktop/CS6200/Assignments/HW2/tempindex/'
RESULT = '/Users/xinshu/desktop/CS6200/Assignments/HW2/result/'

hp = []
total_catalog = {}
start_pos = 0

def main():
    start = timeit.default_timer()
    
    init_catalog_map()
    init_heap()
    mergeIndex()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60),)


def init_catalog_map():
    for f in os.listdir(CATALOG):
        if '.' in f:
            print f
            continue
        
        catalog = []
        filename = CATALOG + f
        fh = open(filename, "r")
        
        for l in fh.readlines():
            catalog.append(l[:-1])
            
        total_catalog[f] = catalog

def init_heap():
    """
    initialize a priority queue store 85 item which are the first item in each catalog
    """
    pos = 0
    for f in sorted(total_catalog):
        push_1st_term_to_hp(f, pos)

def push_1st_term_to_hp(file, pos):
    """
    :param file: catalog key
    :param pos: index of list 
    """
    cata = total_catalog[file][pos]
    term = cata.split(" ")[0]
    heapq.heappush(hp, (term, file, pos))


def mergeIndex():
    """
    merge the temp index to a final index use the priority queue
    """
    tmp_list = []
    while hp:
        entry = heapq.heappop(hp)
        term = entry[0]
        filename = entry[1]
        pos = entry[2]
        
        tmp_string = getTermFromIndex(filename,pos)
        
        if len(tmp_list) == 0:
            tmp_list.append(term)
            tmp_list.append(tmp_string)
        elif term == tmp_list[0]:
            tmp_list.append(tmp_string)
        else:
            writeToIndex(tmp_list)
            del tmp_list[:]
            tmp_list.append(term)
            tmp_list.append(tmp_string)
        
        pos += 1
        if pos < len(total_catalog[filename]):
            push_1st_term_to_hp(filename, pos)

        
def getTermFromIndex(filename, pos):
    """
     read the index from temp index file, which the start pos and length come from catalog dictionary
    :param filename: temp index filename
    :param pos: index in catalog map in that which key is filename
    :return: a string has ids, and poses
    """
    index_file = TEMPINDEX  + filename
    fh = open(index_file, "r")
    start, length = getStartPos(filename, pos)
    fh.seek(start)
    tmp_string = fh.read(length).split(" ", 1)[1][:-1]
    fh.close()
    return tmp_string

def getStartPos(filename, pos):
    """
     get the start and length from catalog dictionary
    :param filename: catalog filename and the same with the dictionary key
    :param pos: the list in value index
    :return: integer, the start and length
    """
    cata = total_catalog[filename][pos]
    start = cata.split(" ")[1]
    length = cata.split(" ")[2]
    return int(start), int(length)


def writeToIndex(tmp_list):
    """
    write the final index to the index file without the term, only have doc_id and poses
    """
    filename = RESULT + "index"
    if not os.path.exists(filename):
        fh = open(filename, "w")
    else:
        fh = open(filename, "a")

    term = tmp_list[0]
    tmp_string = " ".join(tmp_list[1:]) + "\n"
    length = len(tmp_string)
    
    fh.write(tmp_string)
    fh.close()
    writeToCata(term, length)

def writeToCata(term, length):
    """
     write the final catalog to the catalog file with term, start pos, length
    :param term: term
    :param length: string length in index
    """
    global start_pos
    filename = RESULT + "catalog"
    
    if not os.path.exists(filename):
        fh = open(filename, "w")
    else:
        fh = open(filename, "a")
        
    tmp = [term, start_pos, length]
    tmp_string = " ".join(map(str, tmp)) +"\n"
    
    fh.write(tmp_string)
    fh.close()
    start_pos += length


if __name__ == '__main__':
    main()
