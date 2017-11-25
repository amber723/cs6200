import math, operator, string, re, timeit

CRAWLED = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/link_file.txt'
OTHER = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/wt2g_inlinks.txt'
CRAWLED_OUTPUT = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/crawled_top500.txt'
OTHER_OUTPUT = '/Users/xinshu/desktop/CS6200/Assignments/HW4/data/other_top500.txt'

THRESHOLD = 1
LAMBDA = 0.15

class PageRank():
    def __init__(self, adjacent_list, out_links, type):
        self.adjacent_list = adjacent_list
        self.out_links = out_links
        
        self.node_list = sorted(self.adjacent_list.keys())
        self.size = len(self.node_list)
        self.last_vector = {key: 1.0/self.size for key in self.node_list}
        self.sink_links = self.get_sink_links()
        self.LAMBDA = 0.15

        self.type = type
        print 'adjacent_list length: ', len(self.adjacent_list)
        print 'out_links length: ', len(self.out_links)
        print 'size length: ', self.size
        print 'sink_link length: ', len(self.sink_links)


    def get_sink_links(self):
        sink_links = []
        for node in self.node_list:
            if node not in self.out_links:
                sink_links.append(node)
        return sink_links


    def rank(self):
        count = 0
        prev_perplexity = 0
        cur_perplexity = self.perplexity(self.last_vector)
        
        while not self.coverage(prev_perplexity, cur_perplexity):
            sinkPR = 0
            
            for node in self.sink_links:
                sinkPR += self.last_vector[node]
            print "The sink PR is", sinkPR
            
            current_vector = {key: (self.LAMBDA + (1-self.LAMBDA) * sinkPR)/self.size for key in self.node_list}

            for node in self.node_list:
                in_links = self.adjacent_list[node]
    
                for in_link in in_links:
                    if in_link in self.out_links:
                        out_links_len = self.out_links[in_link]
                    else:
                        break
                    pagerank = self.last_vector[in_link]
                    current_vector[node] += (1-self.LAMBDA) * (pagerank/out_links_len)
                    
            vector_sum = sum(current_vector.values())
            print 'vector_sum: ', vector_sum

            for node in current_vector:
                current_vector[node] = current_vector[node]/vector_sum
                
            prev_perplexity = cur_perplexity
            cur_perplexity = self.perplexity(current_vector)
            self.last_vector = current_vector
            
            print "the previous perplexity is", prev_perplexity
            print "the current perplexity is", cur_perplexity
            print "this is the ", count
            count += 1


    def output_result(self):
        output = sorted(self.last_vector.items(), key=operator.itemgetter(1), reverse = True)
        if self.type == 'other':
            fh = open(OTHER_OUTPUT, "w")
        else:
            fh = open(CRAWLED_OUTPUT, "w")
        for i in range(500):
            node = output[i][0]
            rank = output[i][1]
            if node in self.adjacent_list:
                inlinks_len = len(self.adjacent_list[node])
            else:
                inlinks_len = 0
            fh.write('%s %s %s\n'%(node,str(rank), str(inlinks_len)))


    def perplexity(self, vector):
        s = 0
        for node in vector:
            p = vector[node]
            s += p * math.log(p, 2)
        return pow(2, (-1 * s))

    def coverage(self, prev_perplex, cur_perplex):
        diff = abs(prev_perplex - cur_perplex)
        return diff < THRESHOLD

def get_crawled_adjacent_list():
    fh = open(CRAWLED, "r")
    adjacent_list = {}
    out_links = {}

    for line in fh.readlines():
        newline = string.strip(line, "\n")
        newline = string.strip(newline, "\t")
        node = newline.split("\t")[0]
        out_links_len = int(newline.split("\t")[1])
        in_links = newline.split("\t")[2:]
        
        adjacent_list[node] = in_links
        if out_links_len != 0:
            out_links[node] = out_links_len

    print len(out_links)," has out links"
    print "finish input step"
    fh.close()
    return adjacent_list, out_links 

def get_other_adjacent_list():
    fh = open(OTHER, "r")
    adjacent_list = {}
    out_links = {}
    
    for line in fh.readlines():
        node  = line.split()[0]
        in_links = line.split()[1:]
        adjacent_list[node] = in_links
        
        for link in in_links:
            if link in out_links:
                out_links[link] += 1
            else:
                out_links[link] = 1
                
    fh.close()
    return adjacent_list, out_links

def main():
    start = timeit.default_timer()

    other_ad, other_out = get_other_adjacent_list()
    pr1 = PageRank(other_ad, other_out, 'other')
    pr1.rank()
    pr1.output_result()

##    crawl_ad, crawl_out = get_crawled_adjacent_list()
##    pr2 = PageRank(crawl_ad, crawl_out, 'crawl')
##    pr2.rank()
##    pr2.output_result()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60))    

if __name__ == '__main__':
    main()
