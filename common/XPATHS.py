# -*- encoding:utf-8 -*-
"""
    author:lgh
"""

TONGCHENG_DETAIL_APARTMENT_HREF_XPATHS = ('//div[@class="main"]//ul[@class="list"]//li/a//@href',)
TONGCHENG_APARTMENT_NAME_XPATHS = ('//main//div[@class="describe"]//p[@class="head-title"]/text()',
                                   '//div[@class="gray-wrap"]//div[contains(@class, "apartment-info")]//span[@class="name"]/text()')
TONGCHENG_APARTMENT_LABELS_XPATHS = ('//div[@class="gray-wrap"]//ul[@class="house-info-list"]//i/text()',)
TONGCHENG_APARTMENT_BASIC_INFOS_XPATHS = ('//div[@class="gray-wrap"]//ul[@class="house-info-list"]//span/text()',)

ZIROOM_DETAIL_APARTMENT_HREF_XPATHS = ('//ul[@id="houseList"]//div[@class="txt"]//h3//a/@href',)
ZIROOM_RENTAL_LNG_XPATHS = ('//input[@id="mapsearchText"]/@data-lng',)
ZIROOM_RENTAL_LAT_XPATHS = ('//input[@id="mapsearchText"]/@data-lat',)