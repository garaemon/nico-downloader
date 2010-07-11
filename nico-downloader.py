#!/usr/bin/env python
#coding:sjis
"""
usage: nico-downloader --user=USERNAME --passwd=PASSWD myscript_url

this script is inspired by http://d.hatena.ne.jp/lolloo-htn/20090417/1239972394.
"""

import sys
import os
import re
import cgi
import urllib
import urllib2
import cookielib
import xml.dom.minidom
import time
import socket
from optparse import OptionParser, OptionValueError
import subprocess
import codecs

socket.setdefaulttimeout(10)
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

def getids(url,conn):
    ret = []
    data = conn.open(url).read()
    dTree = xml.dom.minidom.parseString(data)

    for itree in dTree.getElementsByTagName('item'):
        smid = itree.getElementsByTagName('link')[0].firstChild.data.strip().split('/')[-1]
        ret.append(smid)
    return ret

def nico_connect(userid, passwd):
    print "connecting to nicovideo..."
    req = urllib2.Request("https://secure.nicovideo.jp/secure/login?site=niconico")
    req.add_data(urllib.urlencode({"mail": userid, "password": passwd}))
    opener.open(req)

def nico_download(smid, user, passwd):
    print "downloading %s" % smid
    while True:
        try:
            time.sleep(10)
            data = urllib.urlopen("http://www.nicovideo.jp/api/getthumbinfo/"+smid).read()
            pTree = xml.dom.minidom.parseString(data)
            videoTitle = pTree.getElementsByTagName("title")[0].firstChild.data
            res = opener.open("http://www.nicovideo.jp/api/getflv/"+smid).read()
            videoURL = cgi.parse_qs(res)["url"][0]
            fname = videoTitle + "." + "mp4"
            opener.open("http://www.nicovideo.jp/watch/"+smid, timeout=120)
            # only download when file does not exists
            if not os.path.exists(fname):
                time.sleep(10)
                res = opener.open(videoURL, timeout=120)
                ext = res.info().getsubtype()
                data = res.read()
                if re.search(r"low$",videoURL):
                    videoTitle = "(LOW)"+videoTitle
                ofh = open(videoTitle+"."+ext,"wb")
                ofh.write(data)
                ofh.close()
                print "Downloaded: %s" % smid
            else:
                print "%s is already downloaded" % smid
            break
        except Exception, e:
            print "error %s" % e
            nico_connect(user, passwd)
            time.sleep(100)

def setup_parser(parser):
    parser.add_option("--user", "-u",
                      dest = "user",
                      default = False,
                      help = "specify your niconico account",
                      action = "store")
    parser.add_option("--passwd", "-p",
                      dest = "passwd",
                      default = False,
                      help = "specify your niconico acount's password",
                      action = "store")

def usage():
    print __doc__ % vars()
    
# main...
if __name__ == "__main__":
    parser = OptionParser()
    setup_parser(parser)
    (options, args) = parser.parse_args(sys.argv[1:])
    # check args
    if not (len(args) == 1 and options.user and options.passwd):
        usage()
        sys.exit(1)
    url = args[0] + "?rss=2.0"
    print "target mylist url => %s" % url
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    nico_connect(options.user, options.passwd)
    smids = getids(url, opener)
    for smid in smids:
        nico_download(smid, options.user, options.passwd)
