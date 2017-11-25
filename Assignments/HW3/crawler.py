#! user/bin/python
from urlparse import urlparse
import urllib2
from lxml import etree
import time, os, timeit
import robotexclusionrulesparser

from frontier import Frontier
from Parser import ParserTarget
from storer import Store

OUTPATH = '/Users/xinshu/desktop/CS6200/Assignments/HW3/data/'
MAX_COUNT = 20100

def main():
    start = timeit.default_timer()
    
    c = Crawler()
    c.initial_seeds()
    c.crawl()

    stop = timeit.default_timer()
    print ('run time: ', int((stop - start)//60), int((stop-start)%60),)

class Crawler:
    '''
    crawling the website, get the text the links in page
    '''
    def __init__(self):
        self.count = 0
        self.last_domain = ''
        self.frontier = Frontier()
        self.store = Store()

    def initial_seeds(self):
        self.frontier.initial_queue()

    def parseRobot(self, domain):
        robot_url = 'http://' + domain + '/robots.txt'
        
        try:
            robot_file = urllib2.urlopen(robot_url).read()
            robot_content = ''
            for l in robot_file.split('\n'):
                if l.replace(' ','') != '':
                    robot_content += l + '\n'
            robot_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
            robot_parser.parse(robot_content)

            try:
                crawler_delay = robot_parser.get_crawl_delay('*')
            except Exception as e:
##                print 'crawler_delay exception: {}'.format(e)
                crawler_delay = None
            
            return robot_parser, crawler_delay
        except Exception as e:
##            print 'robot parse exception: {}'.format(e)
            return None, None

    def crawl(self):
        '''
        pop a url from frontier and get the header, html, text and out links.
        push the out links into frontier and insert them into elasticsearch
        '''
        while self.count < MAX_COUNT:
            level, url = self.frontier.pop_url()

            try:
                current_domain = urlparse(url).netloc

##                if current_domain not in self.frontier.robot_dict and self.frontier.no_robot:
##                    self.frontier.add_robot_dict(url)
##
##                if current_domain in self.frontier.robot_dict and not (self.frontier.robot_dict[current_domain].can_fetch('*', url)): 
##                    continue

                robot_parser, crawler_delay = self.parseRobot(current_domain)
                if robot_parser is not None:
                    if not robot_parser.is_allowed('*', url):
                        print 'not allowed to crawl: {}'.format(url)
                        continue
                    if crawler_delay is not None:
                        time.sleep(crawler_delay)
                
            except Exception as e:
                print 'current_domain_exception: {}'.format(e)
                print url
                continue

            if current_domain == self.last_domain:
                time.sleep(1)
            else:
                self.last_domain = current_domain

            try:
                header, raw_html = self.downloader(url)
            except Exception, e:
                print 'downloader exception: {}'.format(e)
                continue

            try:
                text, title, links = self.parse_url(url, raw_html)
            except Exception as e:
                print 'parse exception: {}'.format(e)
                continue

            if text or links:
                self.count += 1
                out_links = []
                
                for link in links:
                    try:
                        if len(self.frontier.pq) > MAX_COUNT:
                            break
                        if self.frontier.check_push_url(link, url):
                            out_links.append(link)
                    except Exception as e:
                        continue
                
                print 'FINISHED: {}'.format(self.count)

                self.store.insert(self.count, url, header, title, text,
                                  raw_html, [], out_links, level)

                self.write_to_file(self.count, url, header, title, text,
                                  raw_html, out_links, level)
            else:
                continue

        self.frontier.write_in_links()
        self.store.write_urls()
        
    def downloader(self, url):
        '''
        get the response of the url, only keep the page language is english and has text
        :param url: response url
        :return: header, raw html
        '''
        try:
            response = urllib2.urlopen(url, timeout=3)
        except Exception, e:
            print 'urlopen exception {} | {}'.format(url, e)
            raise Exception

        try:
            code = response.getcode()
            if code != 200:
                raise Exception

            header = response.info()
            if not header:
                raise Exception

            if 'content-language' in header:
                if 'en' not in header['content-language']:
                    raise Exception

            if 'content-type' in header:
                if 'text' not in header['content-type']:
                    raise Exception

        except Exception, e:
            print e
            raise Exception

        try:
            raw_html = response.read()
            raw_html = raw_html.decode('utf-8', 'ignore')
        except Exception as e:
            print 'raw_html except: {} | {}'.format(url, e)
            raise Exception
        return str(header), raw_html

    def parse_url(self, url, html):
        '''
        parse the html get it title, cleaned text and canonicalized links
        return: text, title, links
        '''
        try:
            parser = etree.HTMLParser(target=ParserTarget(url),
                                      remove_blank_text=True,
                                      remove_comments=True)
            etree.HTML(html, parser=parser)
            text = ' '.join(parser.target.text_lines)
            title = parser.target.title
            links = parser.target.links
            
        except Exception as e:
            raise Exception
        
        return text, title, links

    def write_to_file(self, count, url, header, title, text,
                                  raw_html, out_links, level):

        output = OUTPATH + str(count//200)
            
        if not os.path.exists(output):
            fh = open(output, "w")
        else:
            fh = open(output, "a")
            
        fh.write('<DOC>\n')
        fh.write('%s\n'%('<DOCNO>' + str(count) + '</DOCNO>'))
        fh.write('%s\n'%('<URL>' + url + '</URL>'))
        fh.write('%s\n'%('<DEPTH>' + str(level) + '</DEPTH>'))
        fh.write('%s\n'%('<HEAD>' + title.encode('ascii','ignore') + '</HEAD>'))
        fh.write('%s\n'%('<HTTPHEADER>\n' + header + '\n</HTTPHEADER>'))
        fh.write('%s\n'%('<OUT_LINKS>\n' + ' '.join(out_links) + '\n</OUT_LINKS>'))
        fh.write('%s\n'%('<TEXT>\n' + text.encode('ascii','ignore') + '\n</TEXT>'))
        fh.write('%s\n'%('<HTML>\n' + raw_html.encode('ascii','ignore') + '\n</HTML>'))        
        fh.write('</DOC>\n')
        fh.close()


if __name__ == '__main__':
    main()
