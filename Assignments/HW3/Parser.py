import urllib2
from lxml import etree
from Canonicalizer import Canonicalizer

class ParserTarget(object):
    
    def __init__(self, base_url):
        self.canon = Canonicalizer(base_url)
        self.in_body = False
        self.clean_once = False
        self.is_title = False
        self.text_lines = []
        self.title = ''
        self.links = []
    
    def start(self, tag, attribute):
        if tag == 'body':
            self.in_body = True
        if self.in_body:
            self.clean_once = not (tag == 'link' or tag == 'script' or tag == 'style')
        if tag == 'title':
            self.is_title = True
        if self.in_body and tag == 'a' and attribute.has_key('href') and len(attribute['href']) > 3:
            self.links.append(self.canon.norms(attribute['href']))

    def end(self, tag):
        if tag == 'body':
            self.in_body = False

    def data(self, data):
        d = data.strip()
        if self.is_title and d:
            self.title = d
            self.is_title = False
        if self.clean_once and d:
            self.text_lines.append(d)
    
    def close(self):
        pass

if __name__ == '__main__':
    
    url = 'http://www.theamericanrevolution.org/DocumentDetail.aspx?document=33'
    
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    
    response = opener.open(url)
    header = response.info()
    
    print header
    
    if 'content-type' in header:
        if 'text' not in header['content-type']:
            print 'NOT text-based page: {}'.format(url)

    html = str(response.read())
    response.close()
    opener.close()
    
    target1 = ParserTarget(url)
    print target1.__dict__
    
    parser = etree.HTMLParser(encoding='utf-8',
                           target = ParserTarget(url),
                           remove_blank_text=True,
                           remove_comments=True)

    etree.HTML(html, parser)

    text = ' '.join(parser.target.text_lines)
    print text[1: 1000]

    title = parser.target.title
    print title

    links = parser.target.links

    for link in links:
        print link

