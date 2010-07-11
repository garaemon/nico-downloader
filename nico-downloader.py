#!/usr/bin/env python
#coding:sjis
"""
usage: nico-downloader.py --user=USERNAME --passwd=PASSWD [OPTIONS] mylist_url
currently supported options are:
  --iphone (convert the movies for iphone using ffmpeg and libx264)

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
import progressbar
import multiprocessing
import yaml

debug = True

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
    if debug:
        print "connecting to nicovideo..."
    req = urllib2.Request("https://secure.nicovideo.jp/secure/login?site=niconico")
    req.add_data(urllib.urlencode({"mail": userid, "password": passwd}))
    opener.open(req)

def nico_download(smid, user, passwd, iphonep):
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
                #if re.search(r"low$",videoURL):
                #    videoTitle = "(LOW)"+videoTitle
                ofh = open(fname)
                ofh.write(data)
                ofh.close()
            else:
                if debug:
                    print "%s is already downloaded" % smid
            try:
                if iphonep:
                    outname = videoTitle + "_iphone" + ".mp4"
                    convert_to_iphone(fname, outname)
            except:
                print "converting %s to iphone is failed" % fname
            break
        except Exception, e:
            if debug:
                print "error %s" % e
            nico_connect(user, passwd)
            time.sleep(100)


def convert_to_iphone(inname, outname):
    if not os.path.exists(outname):
        subprocess.check_call(["ffmpeg", "-y",
                               "-i", inname,
                               "-f", "mp4",
                               "-acodec", "libfaac",
                               "-vcodec", "libx264",
                               "-vpre", "default",
                               "-s", "960x640", "-aspect", "960:640",
                               "-threads", str(multiprocessing.cpu_count()),
                               "-sameq",
                               "-async", "4800",
                               "-dts_delta_threshold", "1",
                               "-qscale", "7",
                               outname])

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
    parser.add_option("--iphone",
                      dest = "iphone",
                      default = False,
                      help = "specify your niconico acount's password",
                      action = "store_true")
    parser.add_option("--config", "-c",
                      dest = "config",
                      default = "~/.niconico")

def usage():
    print __doc__ % vars()

def read_user(config):
    return yaml.load(open(os.path.expanduser(config)).read())['user']
def read_user(config):
    return yaml.load(open(os.path.expanduser(config)).read())['passwd']

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
    widgets = ["downloading: ", progressbar.Percentage(),
               progressbar.Bar()]
    pbar = progressbar.ProgressBar(maxval = len(smids),
                                   widgets = widgets).start()
    if option.user:
        user = option.user
    else:
        user = read_user(option.config)
    if option.passwd:
        passwd = option.passwd
    else:
        user = read_passwd(option.config)
        
    for smid in smids:
        pbar.update(pbar.currval + 1)
        nico_download(smid, user, passwd, options.iphone)
    pbar.finish()
