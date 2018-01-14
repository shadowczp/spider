# coding=utf8
from django.shortcuts import render

# Create your views here.
from urllib.parse import *
from django.http import HttpResponse
import json
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

service_args = []
service_args.append('--load-images=no')  ##关闭图片加载
service_args.append('--disk-cache=yes')  ##开启缓存
service_args.append('--ignore-ssl-errors=true')  ##忽略https错误

dcap = dict(DesiredCapabilities.PHANTOMJS)  # 用来设置UA信息 ,后续此处应该做成UA列表，随机选择UA防止被反爬虫
dcap[
    'phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (iPhone1 02; CPU iPhone OS 11_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 MQQBrowser/8.0.2 Mobile/15B87 Safari/8536.25 MttCustomUA/2 QBWebViewType/1 WKType/1'

driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)  # phantomjs初始化

pattern = re.compile(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')  # 匹配URL

# xpath,第一个是title，第二个是price，因为淘宝页面有很多种，会有不同的xpath，有待继续添加
x_path_list = [
    # taobao
    ('//*[@id="J_newDetail"]/div/div[3]/div[2]/h1/span',
     '//*[@id="J_newDetail"]/div/div[3]/div[3]/div/div[1]/p[1]/span'),
    # .tmall
    ('//*[@id="J_mod4"]/div/div/div', '//*[@id="J_mod5"]/div/div[1]/span[1]/span'),
]
# xpath对应的name .tmall是和taobao一样六个字母，为了后面提取flag方便
x_path_name = ['taobao', '.tmall']
# 将xpath组合成dict
x_path_dict = dict(zip(x_path_name, x_path_list))


def get_title_price(request):
    resp = {'resultCode': 500, 'title': None, 'price': None, 'msg': "失败"}
    item_url = request.GET.get('url', default='');

    print(item_url)
    match = pattern.match(item_url)
    if match:
        url_result = urlparse(item_url)  # 解析出url的域名后面用来判断用哪个xpath
        domain = url_result.netloc
        x_path_flag = domain[len(domain) - 10:len(domain) - 4]
        x_path = x_path_dict.get(x_path_flag)
        if x_path:
            try:
                driver.get(item_url)
                resp['title'] = driver.find_element_by_xpath(x_path[0]).text
                resp['price'] = driver.find_element_by_xpath(x_path[1]).text
                resp['msg'] = '成功'
                resp['resultCode'] = 200
            except BaseException:
                resp['resultCode'] = 400
                resp['msg'] = '解析失败，URL错误或页面对应xpath错误'
            finally:
                return HttpResponse(json.dumps(resp, ensure_ascii=False), content_type="application/json;charset=utf-8")
        else:
            resp['resultCode'] = 600
            resp['msg'] = 'URL不是淘宝的URL'
            return HttpResponse(json.dumps(resp, ensure_ascii=False), content_type="application/json;charset=utf-8")
    else:
        resp['resultCode'] = 500
        resp['msg'] = '不是有效的URL'
        return HttpResponse(json.dumps(resp, ensure_ascii=False), content_type="application/json;charset=utf-8")
