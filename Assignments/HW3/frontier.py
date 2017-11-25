#! user/bin/python
import itertools, urlparse, robotparser, heapq

OUTPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW3/data/'
SEED_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW3/seeds.txt'
FILTER = ['facebook', 'twitter', 'youtube', 'americanheritage']
KEY_WORDS = ['american', 'revolut', 'independ', 'war','u.s', 'us',
             'found', 'father', 'john_adams', 'benjamin_franklin',
             'alexander_hamilton', 'john_jay', 'thomas_jefferson',
             'james_madison', 'george_washington']
MAX_LINKS = 1000

class Frontier:
    '''
    This class manages the frontier. The frontier is a priority queue,
    store the links prepare to crawl, when it need to pop a url out,
    according to their priorities, pop the most priority url out
    '''
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.REMOVED = '<removed-url>'
        self.domain_size = {}
        self.in_links = {}
        self.in_links_detail = {}
        
        self.level = -1
        self.counter = itertools.count()

        self.robot_dict = {}
        self.filter = FILTER
        self.visited = set()
        self.no_robot = set()

    def initial_queue(self):
        in_links = MAX_LINKS
        count = 0
        fh = open(SEED_PATH, "r")
        lines = fh.readlines()
        
        for l in lines:
            url = l[:-1]
            print 'initial url: {}'.format(url)
            
            self.in_links[url] = in_links
            self.in_links_detail[url] = []
            count = next(self.counter)
            
            entry = [self.level, -in_links, count, url]
            self.entry_finder[url] = entry
            heapq.heappush(self.pq, entry)

            self.add_robot_dict(url)
            
        print self.pq
        fh.close()

    def add_robot_dict(self, url):
        '''
        if url domain has robot.txt, add it into robot dictionary,
        if not, add it in the no robot dictionary
        '''
        up = urlparse.urlparse(url)
        domain = up.netloc
        
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url('http://' + domain + '/robots.txt')
            rp.read()
            self.robot_dict[domain] = rp
        except:
            self.no_robot.add(domain)
            

    def check_push_url(self, can_url, parent_url):
        '''
        check if the url could push into the frontier.
        The url should not be visited and should be english url
        also, its domain cannot be in FILTER list
        '''
        try:
            can_url.decode('ascii')
        except Exception,e:
            return False

        for forbidden in self.filter:
            if forbidden in can_url:
                return False
            
        if can_url in self.visited:
            self.in_links_detail[can_url].append(parent_url)
            return True

        if 'https' in can_url:
            temp_url = 'http' + can_url[5:]
            if temp_url in self.visited:
                self.in_links_detail[can_url].append(parent_url)
                return True

        for key in KEY_WORDS:
            if key in can_url.lower():
                self.add_url(can_url, parent_url)
                return True
            
    def add_url(self, url, parent_url):
        '''
        add a url to frontier;
        if the url has been added, add a remove tag on the previous url.
        and fresh the in links count and push the url in the queue
        '''
        level = self.level
        
        if url in self.entry_finder:
            level = self.entry_finder[url][0]
            self.remove_url(url)
            
        if url in self.in_links:
            self.in_links[url] += 1
            if parent_url not in self.in_links_detail[url]:
                self.in_links_detail[url].append(parent_url)
        else:
            self.in_links[url] = 1
            self.in_links_detail[url]= [parent_url]

        count = next(self.counter)
        entry = [level, -self.in_links[url], count, url]
        self.entry_finder[url] = entry
        heapq.heappush(self.pq, entry)

    def remove_url(self, url):
        '''
        give an existing url a remove tag
        '''
        entry = self.entry_finder.pop(url)
        entry[-1] = self.REMOVED

    def pop_url(self):
        '''
        pop the lowest priority url, raise KeyError if it is empty
        :return: the pop url
        '''
        while self.pq:
            self.level, in_links, count, url = heapq.heappop(self.pq)
            if url is not self.REMOVED:
                
                del self.entry_finder[url]
                self.visited.add(url)
                self.level += 1
                
                return self.level, url
            
        raise KeyError('pop from an empty priority queue')

    def write_in_links(self):
        output = OUTPATH + 'in_links'
        fh = open(output, "w")

        for url, lst in self.in_links_detail.iteritems():
            fh.write('%s\n'%('<url>' + url + '</url>'))
            fh.write('%s\n'%('<in_links>' + ' '.join(lst) + '</in_links>'))
            
        fh.close()
            
