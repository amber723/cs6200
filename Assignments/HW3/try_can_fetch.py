##from urlparse import urlparse
##from frontier import Frontier
import robotexclusionrulesparser

##def try_can_fetch(url):
##    
##    try:
##        current_domain = urlparse(url).netloc
##        
##        if current_domain not in frontier.robot_dict and frontier.no_robot:
##            frontier.add_robot_dict(url)
##            print 'robot added'
##            
##        if current_domain in frontier.robot_dict and not (frontier.robot_dict[current_domain].can_fetch('*', url)): 
##            print 'cannot fetch'
##        else:
##            print 'can fetch'
##
##    except Exception as e:
##        print 'current_domain_exception: {}'.format(e)
##
##frontier = Frontier()
##try_can_fetch('https://twitter.com/robots.txt')
##try_can_fetch('https://en.wikipedia.org/wiki/Wikipedia:Benutzersperrung/')

import urllib2
def parseRobot(domain):
    robot_url = '/'.join([domain, 'robots.txt'])
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
            print 'crawler_delay exception: {}'.format(e)
            crawler_delay = None
        
        return robot_parser, crawler_delay
    except Exception as e:
        print 'robot parse exception: {}'.format(e)
        return None

robot_parser, crawler_delay = parseRobot('https://twitter.com')

print crawler_delay
print robot_parser.is_allowed('*', 'https://twitter.com/search/realtime')


