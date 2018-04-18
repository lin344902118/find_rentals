# -*- coding:utf-8 -*-

import random
import time
from collections import OrderedDict

import requests
from lxml import etree

from UserAgents import USER_AGENTS

key = ''

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
    result = requests.get(url, headers=get_header())
    html = etree.HTML(result.text)
    if source == '58':
        hrefs = html.xpath('//div[@class="main"]//ul[@class="list"]//li/a//@href')
    else:
        hrefs = html.xpath('//ul[@id="houseList"]//div[@class="txt"]//h3//a/@href')
    apartments = list()
    locations = list()
    host = url.split('http://')[1].split('/')[0]
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
