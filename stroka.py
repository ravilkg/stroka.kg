#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import csv
import mysql.connector
import misc


def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')

    pages = soup.find('div', class_='paginator').find_all('a', class_='paginator-item')[-2].text.split('#')

    return int(pages[0])

def write_csv(data):
    with open('stroka_csv', 'a') as f:
        writer = csv.writer(f)

        writer.writerow((data['topic_id'],
                          data['title'],
                          data['price'],
                          data['url']))

def write_db_id(data):
    cnx = mysql.connector.connect(**misc.config)
    cursor = cnx.cursor(named_tuple=True)
    cursor.execute("INSERT INTO idapt "
                    "(id) "
                    "VALUES ('"+data['topic_id']+"')")

    cnx.commit()
    cursor.close()
    cnx.close()

def write_db_item(data):
    cnx = mysql.connector.connect(**misc.config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO apt "
                   "(id,title,price,phone,rooms,type_series,floor,floorof,"
                   "description,datepub,datecreate,url,urldiesel) "
                   "VALUES ('" +data['topic_id']+ "','" +data['title']+ "',"
                   "'" +data['price'] + "','" + data['phone'] + "','" +data['rooms']+ "',"
                   "'" +data['type_series'] + "','" + data['floor'] + "',"
                   "'" +data['floor_of']+ "','" +data['description']+ "',"
                   "'" +data['datepub']+ "','" +data['datecreate']+ "',"
                   "'" +data['href']+ "','" +data['href_diesel']+ "')")

    cnx.commit()
    cursor.close()
    cnx.close()



def get_item_data():
    cnx = mysql.connector.connect(**misc.config)
    cursor = cnx.cursor(named_tuple=True)
    cursor.execute("SELECT id FROM idapt")

    results = cursor.fetchall()

    for row in results:

        url = 'http://stroka.kg/?page=topic-view&topic_id=' + str(row.id)
        soup = BeautifulSoup(get_html(url), 'lxml')

        ads = soup.find('div', class_='topic-view')

        for ad in ads:
            try:
                price = ad.find('span', class_='topic-view-best-topic_cost').text.strip()
            except:
                price = '$'
            try:
                title = ad.find('div', class_='topic-best-view-name').text.strip()
            except:
                title = 'title'
            try:
                phone = ad.find('span', class_='topic-view-best-phone').text.strip()
            except:
                phone = '#'
            try:
                rooms = ad.find('span', class_='topic-view-best-topic_rooms').text.strip()
            except:
                rooms = '#'
            try:
                type_series = ad.find('span', class_='topic-view-best-topic_series').text.strip()
            except:
                type_series = '#'
            try:
                floor = ad.find('span', class_='topic-view-best-topic_floor').text.strip()
            except:
                floor = '#'
            try:
                floor_of = ad.find('span', class_='topic-view-best-topic_floor_of').text.strip()
            except:
                floor_of = '#'
            try:
                description = ad.find('p', class_='bb-p').text.strip()
            except:
                description = 'no description'
            try:
                datepub = ad.find('div', class_='topic-view-topic_date_up').text.strip()
            except:
                datepub = 'today'
            try:
                datecreate = ad.find('div', class_='topic-view-topic_date_create_row').text.strip()
            except:
                datecreate = 'today'
            try:
                href = ad.find('a', class_='topic-view-site-link-a').get('href')
            except:
                href = 'www.stroka.kg/#'
            try:
                href_diesel = ad.find('div', class_='topic-view-diesel_id').find('a').get('href')
            except:
                href_diesel = 'www.stroka.kg/#'

            data = {'topic_id': str(row.id),
                    'price': price,
                    'title': title,
                    'phone': phone,
                    'rooms': rooms,
                    'type_series': type_series,
                    'floor': floor,
                    'floor_of': floor_of,
                    'description': description,
                    'datepub': datepub,
                    'datecreate': datecreate,
                    'href': href,
                    'href_diesel': href_diesel}

            write_db_item(data)

    cursor.close()
    cnx.close()
    print('Write to DB is done!')

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')

    ads = soup.find('table', class_='topics-list').find_all('tbody', class_='topics-item')

    for ad in ads:

        try:
            topic_id = ad.get('data')
        except:
            topic_id = 'id'

        data = {'topic_id': topic_id}

        write_db_id(data)

def main():
    url = 'http://stroka.kg/kupit-kvartiru/?topic_rooms[]=3&topic_rooms[]=4&q=&topic_an=on&order=cost&cost_min=&cost_max=&p=0#paginator'
    base_url = 'http://stroka.kg/kupit-kvartiru/?'
    page_part = 'p='
    query_part = 'topic_rooms[]=3&topic_rooms[]=4&q=&topic_an=on&order=cost&cost_min=&cost_max=&'
    paginator = '#paginator'

    total_pages = get_total_pages(get_html(url))

    for i in range(0, total_pages-1):
        url_gen = base_url + query_part + page_part + str(i) + paginator
        html = get_html(url_gen)
        get_page_data(html)

    get_item_data()





if __name__ == '__main__':
    main()