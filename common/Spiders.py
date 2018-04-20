# -*- coding:utf-8 -*-

import random
import time
from collections import OrderedDict
from abc import abstractmethod

import requests
from lxml import etree

from common.UserAgents import USER_AGENTS
from common.XPATHS import *

key = ''


class BaseApartmentSpider(object):

    def __init__(self, url, city):
        self.url = url
        self.city = city
        self.data = self.send_request(url)
        self.html = etree.HTML(self.data)

    def send_request(self, url):
        result = requests.get(url, headers=get_header())
        return result.text

    def get_data_by_xpath(self, xpaths):
        data = list()
        if len(self.html):
            for xpath in xpaths:
                data = self.html.xpath(xpath)
                if data:
                    break
        return data

    @abstractmethod
    def get_apartment_detail_hrefs(self):
        pass

    @abstractmethod
    def get_apartment_name(self):
        pass

    @abstractmethod
    def get_apartment_location(self):
        pass


class TongchengSpider(BaseApartmentSpider):

    def __init__(self, url, city):
        super(TongchengSpider, self).__init__(url=url, city=city)

    def get_apartment_detail_hrefs(self):
        urls = self.get_data_by_xpath(xpaths=TONGCHENG_DETAIL_APARTMENT_HREF_XPATHS)
        host = self.url.split('http://')[1].split('/')[0]
        hrefs = ['http://{host}{href}'.format(host=host, href=url) for url in urls]
        return hrefs

    def get_apartment_name(self):
        name = self.get_data_by_xpath(xpaths=TONGCHENG_APARTMENT_NAME_XPATHS)
        if name:
            name = name[0].replace(' ', '')
        else:
            name = '未知公寓'
        return name

    def get_apartment_location(self):
        labels = self.get_data_by_xpath(xpaths=TONGCHENG_APARTMENT_LABELS_XPATHS)
        infos = self.get_data_by_xpath(xpaths=TONGCHENG_APARTMENT_BASIC_INFOS_XPATHS)
        address = ''
        location = ''
        for index, label in enumerate(labels):
            if '地址' in label:
                address = infos[index]
                break
        if address:
            address = address.split(',')[-1]
            location = get_location(city=self.city, address=address)
        return location


class ZiroomSpider(BaseApartmentSpider):

    def __init__(self, url, city):
        super(ZiroomSpider, self).__init__(url=url, city=city)

    def get_apartment_detail_hrefs(self):
        urls = self.get_data_by_xpath(ZIROOM_DETAIL_APARTMENT_HREF_XPATHS)
        hrefs =['http:{href}'.format(href=url) for url in urls]
        return hrefs

    def get_apartment_name(self):
        return '自如友家'

    def get_apartment_location(self):
        location = list()
        lng = self.get_data_by_xpath(ZIROOM_RENTAL_LNG_XPATHS)[0]
        lat = self.get_data_by_xpath(ZIROOM_RENTAL_LAT_XPATHS)[0]
        if lng and lat:
            location.append(lng)
            location.append(lat)
        return location


def get_ua():
    return random.choice(USER_AGENTS)

def get_header():
    Header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN, zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_ua(),
    }
    return Header

def get_location(city, address):
    url = 'http://restapi.amap.com/v3/geocode/geo?address={address}&city={city}&key={key}'.format(address=address, city=city, key=key)
    result = requests.get(url, headers=get_header())
    data = result.json()
    location = list()
    if data['status'] == '1':
        geocodes = data['geocodes']
        if geocodes:
            location = geocodes[0]['location'].split(',')
    return location

def get_apartments(source, city, url, limit):
    if source == '58':
        Spider = TongchengSpider
    else:
        Spider = ZiroomSpider
    spider = Spider(city=city, url=url)
    hrefs = spider.get_apartment_detail_hrefs()
    apartments = list()
    locations = list()
    for href in hrefs[:limit]:
        new_spider = Spider(city=city, url=href)
        name = new_spider.get_apartment_name()
        location = new_spider.get_apartment_location()
        apartment = dict()
        if location and location not in locations:
            locations.append(location)
            apartment['name'] = name
            apartment['location'] = location
            apartment['url'] = href
            apartments.append(apartment)
        time.sleep(1)
    return apartments


def get_apartments_old(source, city, url, limit):
    result = requests.get(url, headers=get_header())
    html = etree.HTML(result.text)
    if source == '58':
        hrefs = html.xpath('//div[@class="main"]//ul[@class="list"]//li/a//@href')
    else:
        hrefs = html.xpath('//ul[@id="houseList"]//div[@class="txt"]//h3//a/@href')
    host = url.split('http://')[1].split('/')[0]
    apartments = list()
    locations = list()
    for href in hrefs[:limit]:
        if source == '58':
            href = 'http://' + host + href
            apartment = get_apartment_from_58(href)
        else:
            href = 'http:'+href
            apartment = get_apartment_from_ziroom(href)
        if apartment:
            location = apartment.get('location')
            address = apartment.get('address')
            if not location and address:
                location = get_location(city, address)
                if location:
                    apartment.pop('address')
                    apartment['location'] = location
            if location and location not in locations:
                locations.append(location)
                apartments.append(apartment)
        time.sleep(1)
    return apartments

def get_apartment_from_ziroom(url):
    result = requests.get(url, headers=get_header())
    html = etree.HTML(result.text)
    apartment = OrderedDict()
    try:
        apartment['name'] = '自如友家'
        lng = html.xpath('//input[@id="mapsearchText"]/@data-lng')[0]
        lat = html.xpath('//input[@id="mapsearchText"]/@data-lat')[0]
        apartment['url'] = url
        apartment['location'] = [lng, lat]
    except Exception as e:
        print(e)
    return apartment

def get_apartment_from_58(url):
    result = requests.get(url, headers=get_header())
    html = etree.HTML(result.text)
    apartment = OrderedDict()
    try:
        name = html.xpath('//main//div[@class="describe"]//p[@class="head-title"]/text()')
        if not name:
            name = html.xpath('//div[@class="gray-wrap"]//div[contains(@class, "apartment-info")]//span[@class="name"]/text()')
        name = name[0].replace(' ', '')
        labels = html.xpath('//div[@class="gray-wrap"]//ul[@class="house-info-list"]//i/text()')
        infos = html.xpath('//div[@class="gray-wrap"]//ul[@class="house-info-list"]//span/text()')
        address = ''
        for index, label in enumerate(labels):
            if '地址' in label:
                address = infos[index]
                break
        if address:
            address = address.split(',')[-1]
        apartment['name'] = name
        apartment['address'] = address
        apartment['url'] = url
    except Exception as e:
        print(e)
    return apartment
