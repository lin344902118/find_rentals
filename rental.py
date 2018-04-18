# -*- coding:utf-8 -*-
"""
    a rental scrapy
"""

import datetime
import os
import logging
from logging import FileHandler, Formatter

from flask import Flask, render_template, request, jsonify
import pandas as pd

from Spiders import get_apartments

app = Flask(__name__)

key = ''

CITY = {
    '杭州': 'hz',
    '北京': 'bj',
    '上海': 'sh',
    '广州': 'gz',
    '深圳': 'sz',
}

file_handler = FileHandler(filename='rental.log', encoding='utf-8')
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)

@app.route('/')
def index():
    return render_template('map.html', key=key)

@app.route('/get_rentals', methods=['POST'])
def get_rentals():
    city = request.form.get('city')
    source = request.form.get('source')
    assert source in ['58', '自如'], '房源来源错误'
    low_price = request.form.get('low_price')
    high_price = request.form.get('high_price')
    address = request.form.get('address')
    if address:
        if '(' in address:
            address = address.split('(')[0]
        if source == '58':
            if '·' in address:
                address = address.split('·')[-1]
    app.logger.warning('city:{city},low_price:{low_price},high_price:{high_price},address:{address}'.format(city=city, low_price=low_price,
                                                                                                            high_price=high_price, address=address))
    limit = request.form.get('limit')
    if not limit:
        limit = 5
    result = dict()
    try:
        if city:
            city_short = CITY[city]
            url = get_url(source, address, city_short, high_price, low_price)
            app.logger.warning('url:{url}'.format(url=url))
            apartments = get_apartments(source, city, url, int(limit))
            save_apartments(apartments)
            app.logger.warning(apartments)
            result['ret'] = 0
            result['data'] = apartments
            result['status'] = 'success'
    except Exception as e:
        app.logger.error(str(e))
        result['ret'] = 1000
        result['status'] = 'failed'
        result['message'] = str(e)
    return jsonify(result)


def get_url(source, address, city_short, high_price, low_price):
    if source == '58':
        url = 'http://{city}.58.com/pinpaigongyu/'.format(city=city_short)
        if low_price and high_price:
            url += '?minprice={low_price}_{high_price}'.format(low_price=low_price, high_price=high_price)
        if address:
            url += '&key={key}'.format(key=address)
    else:
        if city_short == 'bj':
            city_short = 'www'
        if low_price and high_price:
            url = 'http://{city}.ziroom.com/z/nl/z2-r{low_price}TO{high_price}.html'.format(city=city_short, low_price=low_price, high_price=high_price)
        else:
            url = 'http://{city}.ziroom.com/z/nl/z2-r2.html'
        if address:
            url += '?qwd={key}'.format(key=address)
    return url

def save_apartments(apartments):
    datas = [a.values() for a in apartments]
    cwd = os.getcwd()
    now = datetime.datetime.now()
    file_dir = os.path.join(cwd, 'static/{}.csv'.format(datetime.datetime.strftime(now, '%Y-%m-%d')))
    dataframe = pd.DataFrame(datas, columns=['公寓名称','URL','经纬度'])
    dataframe.to_csv(file_dir, encoding='utf-8')


if __name__ == '__main__':
    app.run()