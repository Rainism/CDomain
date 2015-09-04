#__author__ = 'croxy'
# -*- coding: UTF-8 -*-
#!/usr/bin/python

import requests
import re
import optparse
import sys
import threading
import Queue
import time



header={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection':'keep-alive'
        }


class CDomain:

    def __init__(self, target, threads_num):
        self.target = target.strip()
        self.threads_num = threads_num
        self.lock = threading.Lock()
        #outfile
        self._getpage()


    def _getpage(self):
        target = self.target
        self.queue = Queue.Queue()
        urls = []
        targets = target.split('-')
        mubiao = targets[0].split('.')[0]+'.'+targets[0].split('.')[1]+'.'+targets[0].split('.')[2]+'.'
        head = targets[0]
        final = mubiao+targets[1]
        last = int(final.split('.')[3])
        first = int(head.split('.')[3])
        while (first <= last):
            try:
                ip = mubiao+str(first)
                url = "https://www.bing.com/search?q=IP%3A{ip}&go=%E6%8F%90%E4%BA%A4&qs=n&form=QBLH&pq=ip%3A{ip}&sc=0-0&sp=-1&sk=&cvid=035319429b334e5e934d677d00f8ad13" .format(ip=ip)
                self.queue.put(url)
                q = requests.get(url, headers=header)
                text = q.content
            #print text
                match = re.findall(r'first=(.*?)&amp;',text)
                if match:
                    for i in range(len(match)):
                        domainpage = "https://www.bing.com/search?q=IP%3A{ip}&go=%E6%8F%90%E4%BA%A4&qs=n&form=QBLH&pq=ip%3A{ip}&sc=0-0&sp=-1&sk=&cvid=035319429b334e5e934d677d00f8ad13&first={page}&FORM=PERE" .format(ip=ip,page=match[i])
                        self.queue.put(domainpage)

            except Exception,e:
                pass
            first = first +1



    def _getdomain(self):
        while self.queue.qsize() > 0:
            url = self.queue.get(timeout=1.0)
            #print url
            domain = []
            try:
                ip = re.findall(r'3A(.*?)&',url)[0]
                q = requests.get(url, headers=header)
                text = q.content
                regx = re.findall(r'<cite>(.*?)</cite>',text)
                if regx[0] != '':
                #print regx
                    for i in range(len(regx)):
                        try:
                            domains = regx[i].split('/')[0]
                        #print domains
                            domain.append(domains)
                        except Exception,e:
                            domain.append(regx[i])

                #print domain
                    print '''ip:{ip}
-------------------------------------------
{domain}
-------------------------------------------
'''.format(ip=ip, domain=domain)
            except Exception,e:
                pass

    def run(self):
        self.start_time = time.time()
        for i in range(self.threads_num):
            t = threading.Thread(target=self._getdomain, name=str(i))
            t.start()


if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options] 202.202.43.1-254')
    parser.add_option('-t', '--threads', dest='threads_num',
              default=10, type='int',
              help='Number of threads. default = 10')
   # parser.add_option('-o', '--output', dest='output', default=None,
   #          type='string', help='Output file name. default is {target}.txt')

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    d = CDomain(target=args[0],threads_num=options.threads_num)
    d.run()