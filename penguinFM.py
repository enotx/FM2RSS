#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-25 15:40:23
# @Author  : Zhidong Xia (enotxtone@gmail.com)
# @Link    : http://enotx.com
# @Version : 0.1

import os
import requests
import pickle
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import json
import datetime

# 文件保存的
DIR = "/var/www/html/rss/"
# DIR = "./"
HOST = "http://enotx.com/rss/"

FILE_LIMIT = 3

HEADERS = {
    'authority': 'fm.qq.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

ENV = 'prod'



## 需要爬新的频道的话，只需要更改下面的配置即可
params_1 = (
    ('aid', 'rd0020t4dD2D1xFY'),
)

fm_list = {"第一财经周刊": {'params': params_1, "img": "http://imgcache.qq.com/fm/photo/album/rmid_album_240/F/Y/0020t4dD2D1xFY.jpg"}}



def getPlaylist(p):
    ## 把请求保存为pickle用于调试
    if ENV == 'test':
        response = pickle.load(open( "r.pkl", "rb" ))
    elif ENV == 'pre':
        response = requests.get('https://fm.qq.com/luobo/radio', headers=HEADERS, params=p)
        pickle.dump(response, open( "r.pkl", "wb" ) )
    elif ENV == 'prod':
        response = requests.get('https://fm.qq.com/luobo/radio', headers=HEADERS, params=p)
    soup = BeautifulSoup(response.text, 'html.parser')

    raw_src_lines = soup.prettify().splitlines()
    data = ''

    ## 企鹅FM的音频信息主要在“window.__INITIAL_STATE__”中，需要解析这个大json
    for i in raw_src_lines:
        if i.strip().startswith('window.__INITIAL_STATE__'):
            data = i
            break
    data = json.loads(data[28:])

    return data["syncData"]["albumPageData"]["showList"]["showList"][:FILE_LIMIT]



if __name__ == '__main__':
    for i in fm_list.keys():
        target_fm = fm_list[i]['params']
        playlist = getPlaylist(p = target_fm)

        #下载最近的一个音频
        a = playlist[0]
        doc = requests.get(a["share"]["dataUrl"], headers=HEADERS)
        if not os.path.exists(DIR + i):
            os.makedirs(DIR + i)

        with open(DIR + i + "/" + a["showID"]+'.m4a', 'wb') as f:
            f.write(doc.content)

        #生成feed xml
        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title(i)
        fg.author( {'name':'enotx','email':'enotxtone@gmail.com'} )
        fg.link( href=HOST, rel='alternate' )
        fg.logo(fm_list[i]["img"])
        fg.subtitle("第一财经周刊")
        fg.link( href=HOST, rel='self' )
        fg.language('zh')
        fg.updated(datetime.datetime.now(datetime.timezone.utc))

        fg.podcast.itunes_category('Technology', 'Podcasting')

        # 倒序遍历，可以使新的PODCAST排在最近
        for j in reversed(playlist):
            fe = fg.add_entry()
            fe.id(HOST+i+'/'+j["showID"]+'.m4a')
            fe.title(j["share"]["title"])
            fe.description(j["share"]["title"])
            fe.enclosure(HOST+i+'/'+j["showID"]+'.m4a', 0, 'audio/mp4')

        fg.rss_str(pretty=True)
        fg.rss_file(DIR + i + '.xml')

        ## 清理陈旧的音频文件
        files_to_reserve = [f["showID"] for f in playlist]
        for f in os.listdir(DIR+i):
            if os.path.splitext(f)[0] not in files_to_reserve:
                os.remove(DIR + i + "/" + f)

