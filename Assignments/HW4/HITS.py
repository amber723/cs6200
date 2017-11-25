import string, math, operator,timeit

TOP1000 = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/top1000.urls.txt'
INLINKS = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/link_file.txt'
TOPHUB = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/top500_hub.txt'
TOPAUT = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/top500_aut.txt'

root = []
base = set()
all_in_links_map = {}
in_links_map = {}
out_links_map = {}
D = 50
THRESHOLD = 0.1

def create_root_set():
    global base
    fh = open(TOP1000, "r")
    for line in fh.readlines():
        line = string.strip(line, '\n')
        root.append(line)
    fh.close()
    base = set(root)

def read_in_links_file():
    fh = open(INLINKS, "r")
    
    for l in fh.readlines():
        l = string.strip(l, "\n")
        newline = string.strip(l, "\t")
        node = newline.split("\t")[0]
        in_links = newline.split("\t")[2:]
        all_in_links_map[node] = in_links
        
    print len(all_in_links_map)
    fh.close()


def create_base_set():
    add_out_links()
    add_in_links()
    create_in_links_map()

def create_in_links_map():
    for node in base:
        if node not in all_in_links_map:
            continue
        in_links = all_in_links_map[node]
        for in_link in in_links:
            if in_link in root:
                if node not in in_links_map:
                    in_links_map[node] = []
                    in_links_map[node].append(in_link)
                else:
                    in_links_map[node].append(in_link)
    print "the in links map is", len(in_links_map)


def add_out_links():
    for node in all_in_links_map:
        in_links = all_in_links_map[node]
        for in_link in in_links:
            if in_link in root:
                if in_link not in out_links_map:
                    out_links_map[in_link] = set()
                    out_links_map[in_link].add(node)
                else:
                    out_links_map[in_link].add(node)
                base.add(node)
    print "the out links map is", len(out_links_map)
    print "add", len(base), "out links to base"

def add_in_links():
    global D
    for node in all_in_links_map:
        if node in root:
            in_links = all_in_links_map[node]
            if len(in_links) > 50:
                for i in range(50):
                    base.add(in_links[i])
            else:
                for link in in_links:
                    base.add(link)
    print "add", len(base), "in links to base"

def rank():

    hub = {key: 1.0 for key in out_links_map}
    aut = {key: 1.0 for key in in_links_map}

    count = 0
    pre_hub_perplexity = 0
    pre_aut_perplexity = 0
    cur_hub_perplexity = perplexity(hub)
    cur_aut_perplexity = perplexity(aut)
    
    while not convergence(pre_hub_perplexity, cur_hub_perplexity,
                          pre_aut_perplexity, cur_aut_perplexity):

        for node in aut:
            aut[node] = sum(hub[link] for link in in_links_map[node])
        aut = normalize(aut)
        
        for node in hub:
            hub[node] = sum(aut[link] for link in out_links_map[node])
        hub = normalize(hub)

        pre_hub_perplexity = cur_hub_perplexity
        pre_aut_perplexity = cur_aut_perplexity

        cur_hub_perplexity = perplexity(hub)
        cur_aut_perplexity = perplexity(aut)

        print "This is turn", count
        count += 1

    output_result(hub, aut)

def perplexity(vector):
    s = 0
    for node in vector:
        p = vector[node] ** 2
        s += p * math.log(p, 2)
    return pow(2, (-1 * s))

def convergence(pre_hub_perplexity, cur_hub_perplexity,
                pre_aut_perplexity, cur_aut_perplexity):
    print "the pre hub, pre aut is", pre_hub_perplexity, pre_aut_perplexity
    print "the cur hub, cur aut is", cur_hub_perplexity, cur_aut_perplexity
    diff_hub = abs(pre_hub_perplexity - cur_hub_perplexity)
    diff_aut = abs(pre_aut_perplexity - cur_aut_perplexity)

    return max(diff_aut, diff_hub) < THRESHOLD

def normalize(vector):
    sum_m = 0
    for node in vector:
        sum_m += vector[node] ** 2
    norm = math.sqrt(sum_m)
    
    for node in vector:
        norm_value = float(vector[node])/norm
        vector[node]=norm_value
    return vector


def output_result(hub, aut):
    sort_hub = sorted(hub.items(), key=operator.itemgetter(1), reverse = True)
    sort_aut = sorted(aut.items(), key=operator.itemgetter(1), reverse = True)
    
    hubfile = open(TOPHUB, "w")
    for i in range(500):
        node = sort_hub[i][0]
        score = sort_hub[i][1]
        outlink_len = len(out_links_map[node])
        hubfile.write('%s\t%s\t%s\n'%(node, score, outlink_len))
        
    autfile = open(TOPAUT,"w")
    for i in range(500):
        node = sort_aut[i][0]
        score = sort_aut[i][1]
        inlink_len = len(in_links_map[node])
        autfile.write('%s\t%s\t%s\n'%(node, score, inlink_len))
        
    hubfile.close()
    autfile.close()

def main():
    start = timeit.default_timer()
    
    create_root_set()
    read_in_links_file()
    create_base_set()

    rank()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60))

if __name__ == '__main__':
    main()
