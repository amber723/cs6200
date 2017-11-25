from urlparse import urlparse, urlunparse
from urllib import unquote
from string import *
import re

class Canonicalizer(object):
    
    _collapse = re.compile('([^/]+/\.\./?|/\./|//|/\.$|/\.\.$)')
    _server_netloc = re.compile('^(?:([^\@]+)\@)?([^\:]+)(?:\:(.+))?$')
    _default_port = {'http': '80', 'https': '443', 'gopher': '70', 'news': '119',
                     'snews': '563', 'nntp': '119', 'snntp': '563',
                     'ftp': '21', 'telnet': '23', 'prospero': '191'}
    _relative_schemes = ['http', 'https', 'news', 'snews', 'nntp',
                         'snntp', 'ftp', 'file', '']

    def __init__(self, url):
        self.parent_url = url
    
    def norms(self, url):
        """
        given a string URL, return its normalized form
        """
        return urlunparse(self.norm(urlparse(url)))
    
    def norm(self, urltuple):
        """
        given a six-tuple URL, return its normalised form
        """
        (scheme, netloc, path, parameters, query, fragment) = urltuple
        
        if scheme == '' or scheme == 'https':
            scheme = 'http'
        scheme = lower(scheme)
        
        if netloc:
            userinfo, host, port = self._server_netloc.match(netloc).groups()
            if host[-1] == '.':
                print ('host has . behinde: ', host)
                host = host[:-1]
            netloc = lower(host)
            
            if userinfo:
                print ('netloc has userinfo', userinfo)
                netloc = "%s@%s" % (userinfo, netloc)
            if port and port != self._default_port.get(scheme, None):
                netloc = "%s:%s" % (netloc, port)
                
        if scheme in self._relative_schemes:
            new_path = self._collapse.sub('/', path, 1)
            while new_path != path:
                path = new_path
                new_path =  self._collapse.sub('/', path, 1)
    
        if netloc == '':
            p_tuple = urlparse(self.parent_url)
            if '../' in path:
                tails = split(p_tuple.path, '/')
                try:
                    del tails[-1]
                    del tails[-1]
                except IndexError:
                    pass
                    log.warning('absolute path transform failed for parent:{} and {}'.format(p_tuple.path, path))
                path = '/'.join(tails) + path.replace('../', '')
            scheme = p_tuple.scheme
            netloc = p_tuple.netloc

        path = unquote(path)
        return scheme, netloc, path, parameters, query, ''

if __name__ == '__main__':
    
    url1 = 'HTTP://www.Example.com/SomeFile.html'   
    url2 = 'http://www.example.com:80/SomeFile.html'
    url3 = '../c.html'
    url4 = 'http://www.example.com/a.html#anything'
    url5 = 'http://www.example.com//a.html'
    url6 = 'http://www.example.com/a/b/../c.html'
    url7 = '/topic/history.html'
    url8 = '/h2'
    url9 = '#'
    url10 = ''
    
    can = Canonicalizer('http://www.example.com/a/b.html')
    
    print can.norms(url1)
    print can.norms(url2)
    print can.norms(url3)
    print can.norms(url4)
    print can.norms(url5)
    print can.norms(url6)
    print can.norms(url7)
    print can.norms(url8)
    print can.norms(url9)
    print can.norms(url10)
