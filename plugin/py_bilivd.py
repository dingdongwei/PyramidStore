# coding=utf-8
# !/usr/bin/python
import sys

sys.path.append('..')
from base.spider import Spider
import json
import requests
from requests import session, utils
import os
import time
import base64


class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "哔哩"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "Zard": "Zard",
            "玩具汽车": "玩具汽车",
            "儿童": "儿童",
            "幼儿": "幼儿",
            "儿童玩具": "儿童玩具",
            "昆虫": "昆虫",
            "动物世界": "动物世界",
            "纪录片": "纪录片",
            "相声小品": "相声小品",
            "搞笑": "搞笑",
            "假窗-白噪音": "窗+白噪音",
            "演唱会": "演唱会"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        if (filter):
            result['filters'] = self.config['filter']
        return result

    def homeVideoContent(self):
        result = {
            'list': []
        }
        return result

    cookies = ''

    def getCookie(self):
        # 在cookies_str中填入会员或大会员cookie，以获得更好的体验。
        cookies_str = "buvid3=DFE11A98-AE03-33F3-5E2D-7E95B9DCC60059298infoc; _uuid=3A2410224-32EB-C10AF-D1052-F91558671088358215infoc; blackside_state=1; rpdid=|(um|kRY~|JR0J'uYJmJkJ|~); CURRENT_BLACKGAP=1; CURRENT_QUALITY=80; CURRENT_FNVAL=2000; PVID=2; innersign=0; b_nut=100; i-wanna-go-back=-1; b_ut=7; b_lsid=52107CA7D_184580B9E2F; bsource=search_baidu; buvid4=25A71F89-198C-3488-34B9-11EF56C8067A69956-022110900-vrdTEqiJKxsFe4OXY793aw%3D%3D; fingerprint=c674be439801a2e72ec8af9f056f6ceb; buvid_fp_plain=undefined; SESSDATA=77b4fb9f%2C1683476506%2C874e6%2Ab1; bili_jct=20b26fefd5f168b3cbf8099fc18f3b4c; DedeUserID=32091585; DedeUserID__ckMd5=ff17d50a5b7fefa3; sid=7bm9ns7c; buvid_fp=f6ff758274f6b4c2925f7c52365d61f0"
        cookies_dic = dict([co.strip().split('=') for co in cookies_str.split(';')])
        rsp = session()
        cookies_jar = utils.cookiejar_from_dict(cookies_dic)
        rsp.cookies = cookies_jar
        content = self.fetch("http://api.bilibili.com/x/web-interface/nav", cookies=rsp.cookies)
        res = json.loads(content.text)
        if res["code"] == 0:
            self.cookies = rsp.cookies
        else:
            rsp = self.fetch("https://www.bilibili.com/")
            self.cookies = rsp.cookies
        return rsp.cookies

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}&page={1}'.format(tid, pg)
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies)
        content = rsp.text
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['result']
        for vod in vodList:
            aid = str(vod['aid']).strip()
            title = vod['title'].replace("<em class=\"keyword\">", "").replace("</em>", "").replace("&quot;", '"')
            img = 'https:' + vod['pic'].strip()
            remark = str(vod['duration']).strip()
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": remark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def cleanSpace(self, str):
        return str.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')

    def detailContent(self, array):
        aid = array[0]
        url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)
        rsp = self.fetch(url, headers=self.header)
        jRoot = json.loads(rsp.text)
        jo = jRoot['data']
        title = jo['title'].replace("<em class=\"keyword\">", "").replace("</em>", "")
        pic = jo['pic']
        desc = jo['desc']
        timeStamp = jo['pubdate']
        timeArray = time.localtime(timeStamp)
        year = str(time.strftime("%Y", timeArray))
        dire = jo['owner']['name']
        typeName = jo['tname']
        remark = str(jo['duration']).strip()
        vod = {
            "vod_id": aid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": typeName,
            "vod_year": year,
            "vod_area": "",
            "vod_remarks": remark,
            "vod_actor": "",
            "vod_director": dire,
            "vod_content": desc
        }
        ja = jo['pages']
        playUrl = ''
        for tmpJo in ja:
            cid = tmpJo['cid']
            part = tmpJo['part'].replace("#", "-")
            playUrl = playUrl + '{0}${1}_{2}#'.format(part, aid, cid)

        vod['vod_play_from'] = 'B站视频'
        vod['vod_play_url'] = playUrl

        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        header = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}'.format(key)
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies,headers=header)
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] != 0:
            rspRetry = self.fetch(url, cookies=self.getCookie())
            content = rspRetry.text
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['result']
        for vod in vodList:
            aid = str(vod['aid']).strip()
            title = vod['title'].replace("<em class=\"keyword\">", "").replace("</em>", "").replace("&quot;", '"')
            img = 'https:' + vod['pic'].strip()
            remark = str(vod['duration']).strip()
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": remark
            })
        result = {
            'list': videos
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}

        ids = id.split("_")
        url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid={1}&qn=116'.format(ids[0], ids[1])
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies)
        jRoot = json.loads(rsp.text)
        jo = jRoot['data']
        ja = jo['durl']

        maxSize = -1
        position = -1
        for i in range(len(ja)):
            tmpJo = ja[i]
            if maxSize < int(tmpJo['size']):
                maxSize = int(tmpJo['size'])
                position = i

        url = ''
        if len(ja) > 0:
            if position == -1:
                position = 0
            url = ja[position]['url']

        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        result["contentType"] = 'video/x-flv'
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self, param):
        return [200, "video/MP2T", action, ""]
