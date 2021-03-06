#!/usr/bin/python2
# -*- coding: utf-8 -*-
import json
import urllib2
import requests
import random
from bs4 import BeautifulSoup
from weibo import APIClient
import os
import sys
import cookielib
__version__ = '1.0'
__author__ = 'MongoliaNavy'

APP_KEY = '4021901498'  # app key
APP_SECRET = '19ca8c3661c75b1ff541f8ab3ae4d7a4'  # app secret
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'  # callback url

# 获取微博授权，手动操作


def getclient():
    client = APIClient(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        redirect_uri=CALLBACK_URL)
    url = client.get_authorize_url()
    pwd=sys.path[0]
    cookie_jar = cookielib.MozillaCookieJar()
    cookies = open('cookies.txt').read()
    for cookie in json.loads(cookies):  
        print cookie['name']  
        cookie_jar.set_cookie(cookielib.Cookie(version=0, name=cookie['name'], value=cookie['value'], port=None, port_specified=False, domain=cookie['domain'], domain_specified=False, domain_initial_dot=False, path=cookie['path'], path_specified=True, secure=cookie['secure'], expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False))
    req = urllib2.Request("https://api.weibo.com/oauth2/authorize?redirect_uri=https%3A//api.weibo.com/oauth2/default.html&response_type=code&client_id=4021901498")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    response = opener.open(req)
    a=response.geturl()
    code = a.split('=')[1].rstrip()
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)
    return client


def getweather():
    weather = requests.get("http://m.weather.com.cn/mweather/101170101.shtml")
    chuanyi = requests.get(
        "http://m.weather.com.cn/mzs/101170101.shtml?flag=ct")
    kongqi = requests.get("http://m.weather.com.cn/maqi/101170101.shtml")
    aqi = requests.get("http://www.pm25.com/yinchuan.html")
    soup4 = BeautifulSoup(aqi.text, "lxml")
    soup1 = BeautifulSoup(weather.text, "lxml")
    soup2 = BeautifulSoup(chuanyi.text, "lxml")
    today = soup1.find_all('div', class_='days7')[0].find_all('li')[0]
    wendu = today.find('span').text.encode('UTF-8')
    tianqi2 = ""
    if len(today.find_all('img')) == 2:
        tianqi2 = today.find_all('img')[1].attrs['alt'].encode('UTF-8')
    tianqi1 = today.find_all('img')[0].attrs['alt'].encode('UTF-8')
    rand = random.randint(0, 8)
    tip = soup2.find_all('div', class_='tips')[rand].find('p').text.encode('UTF-8')
    kongqidict = {
        "优": "空气很好，可以外出活动，呼吸新鲜空气，拥抱大自然！",
        "良": "空气好，可以外出活动，除极少数对污染物特别敏感的人群以外，对公众没有危害！",
        "轻度污染": "空气一般，老人、小孩及对污染物比较敏感的人群会感到些微不适！",
        "中度污染": "空气较差，老人、小孩及对污染物比较敏感的人群会感到不适！",
        "重度污染": "空气差，适当减少外出活动，老人、小孩出门时需做好防范措施！",
        "严重污染": "空气很差，尽量不要外出活动!"}
    zhiliang = soup4.find("div", class_="bi_location_content_active hide").find(
        'a').attrs["qua"].encode('UTF-8')
    tip2 = kongqidict[zhiliang]
    if tianqi2 != "":
        if tianqi1 == tianqi2:
            tianqi = tianqi1
        else:
            tianqi = tianqi1 + "转" + tianqi2
    else:
        tianqi = tianqi1
    weibotext = "#银川#今天天气:" + tianqi + "，温度:" + wendu + \
        "，空气质量:" + zhiliang + "，" + tip2 + "喵了个咪温馨提示," + tip

    return weibotext


def getforecast():
    weather = requests.get("http://m.weather.com.cn/mweather/101170101.shtml")
    soup1 = BeautifulSoup(weather.text, "lxml")
    weatherlist = []
    daylist = []
    wendulist = []
    tianqilist = []
    i = 0
    for temp in soup1.find_all('div', class_='days7')[0].find_all('li'):
        temp2 = ""
        if len(temp.find_all('img')) == 2:
            temp2 = temp.find_all('img')[1].attrs['alt'].encode('UTF-8')
        temp1 = temp.find_all('img')[0].attrs['alt'].encode('UTF-8')
        if temp2 != "":
            if temp1 == temp2:
                weatherlist.append(temp1)
            else:
                weatherlist.append(temp1 + "转" + temp2)
        else:
            weatherlist.append(temp1)
        wendulist.append(temp.find('span').text.encode('UTF-8'))
        daylist.append(temp.find('b').text.encode('UTF-8'))
        i = i + 1
    for i in range(1, 7):
        tianqilist.append(
            daylist[i] +
            ":" +
            weatherlist[i] +
            "，气温:" +
            wendulist[i])
    weibotext = "喵了个咪为您发布#银川#天气预报："
    for i in range(0, 6):
        weibotext = weibotext + tianqilist[i] + "。"
    return weibotext


def getimg():
    blog = requests.get("http://cendalirit.blogspot.com/")
    soup = BeautifulSoup(blog.text, "lxml")
    blogurl = soup.find(
        'div',
        class_="post hentry uncustomized-post-template").find('h3').find('a').attrs['href']
    blog = requests.get(blogurl)
    soup = BeautifulSoup(blog.text, 'lxml')
    image = soup.find(
        'div',
        class_='post hentry uncustomized-post-template').find('meta').attrs['content']
    cmd = 'wget -O /tmp/1.jpg ' + image
    os.popen(cmd)


def posttext(client):
    text = getforecast()
    utext = unicode(text, "UTF-8")
    client.statuses.update.post(status=utext)


def postimg(client):
    getimg()
    f = open('/tmp/1.jpg', 'rb')
    text = getweather()
    r = client.statuses.upload.post(status=text, pic=f)
    f.close()  # APIClient
    os.popen("rm -f /tmp/1.jpg")
if __name__ == '__main__':
    client = getclient()
    if sys.argv[1] == 'morning':
        postimg(client)
    elif sys.argv[1] == 'night':
        posttext(client)
