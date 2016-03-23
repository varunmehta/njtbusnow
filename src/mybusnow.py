'''
The information we need to fetch out of this page.

We'll create an ES index per month, if the data gets too huge, then might move it to a smaller set.
Also the shard count is set to 1 for now.

Cron configuration
==================

# The cron job is supposed to run every minute from 5am to 11am

1 5-11 * * * /path/to/python file




'''

import re
import time
from time import strftime

import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://mybusnow.njtransit.com/bustime/wireless/html/eta.jsp?route=---&direction=---&displaydirection=---&stop=---&id='
INDEX_PREFIX = 'mybusnow'
INDEX_NAME = INDEX_PREFIX + '-' + strftime("%Y-%m", time.localtime())
STOP_IDS = [12648, 12655, 13371, 12049, 12070, 12046, 12067, 11787, 11791, 31858]


def parse_html(stop_id):
    mybusnow_json = '{'
    print(BASE_URL + str(stop_id))
    html_page = requests.get(BASE_URL + str(stop_id))
    # html_page = open("../test/eta.html", "r")
    html_text = html_page.text
    html_text = strip_html_whitespace(html_text)
    soup = BeautifulSoup(html_text, "lxml")

    # First parse all the bus related information.
    ps = soup.find_all('p', limit=3)
    mybusnow_json = parse_rt_info(mybusnow_json, ps)

    # <hr/> works as line seperators between buses, so that can be used to demarcate buses.
    hrs = soup.find_all('hr')
    mybusnow_json += '"buses": ['
    mybusnow_json = parse_bus(mybusnow_json, hrs)
    mybusnow_json += "]"
    mybusnow_json += "}"

    return mybusnow_json


def parse_rt_info(mybusnow_json, ps):
    """
    count = 0 - skip
    count = 1 - Time
    count = 2 - Route info
    :param ps:
    :return:
    """
    count = 0
    for p in ps:

        if count == 0:
            # This should print "Welcome to NJT MyBus Now", so skip and move on.
            count += 1
            continue

        # Put all the document header info here;
        if count == 1:
            count += 1
            currently = p.next_element
            mybusnow_json += '"request_datetime":' + '"' + strftime("%Y-%m-%dT%H:%M%Z", time.localtime()) + '",'
            mybusnow_json += '"page_time":' + '"' + currently[10:].strip() + '",'

            continue

        if count == 2:
            count += 1

            rt = p.next_element
            # mybusnow_json += '"selected_route":' + '' + rt[15:].strip() + ','
            # direction = rt.next_sibling.next_element
            # mybusnow_json += '"selected_direction":' + '"' + direction[19:].strip() + '",'
            # stop = direction.next_sibling.next_element
            mybusnow_json += '"selected_stop":' + '"' + rt[14:].strip() + '",'
            stop_no = rt.next_sibling.next_element
            mybusnow_json += '"selected_stop_number":' + '' + stop_no[16:].strip() + ','

    return mybusnow_json


def parse_bus(mybusnow_json, hrs):
    """
    This is a little manual more than programatic, need to get better at regex to parse this cleaner, it does next_sibling and on to parse the info and get it.
    :param hrs:
    :return:
    """

    hr_size = len(hrs)
    count = 0

    for hr in hrs:
        # After the last hr, it is just links to the page.
        if count == hr_size - 1:
            break
        mybusnow_json += '{'
        bus_rt_no = hr.next_sibling
        if ('No arrival times available') in bus_rt_no or (
        'No service is scheduled for this stop at this time') in bus_rt_no:
            mybusnow_json += '}'
            break

        mybusnow_json += '"bus_route_number":' + '' + bus_rt_no.text[1:].strip() + ','
        bus_rt_name = bus_rt_no.next_sibling
        mybusnow_json += '"bus_route_name":' + '"' + bus_rt_name.strip() + '",'
        bus_eta = bus_rt_name.next_sibling

        # warning: sometimes the eta is also shown as < 1 min, need to handle that scenario still.
        mybusnow_json += '"eta":' + '' + bus_eta.text[:-3].strip() + ','
        bus_no = bus_eta.next_sibling.next_sibling.text
        mybusnow_json += '"bus_no":' + '' + bus_no[5:-1].strip() + ''
        mybusnow_json += '}'
        if count < hr_size - 2:
            mybusnow_json += ','
        count += 1

    return mybusnow_json


def strip_html_whitespace(html_text):
    """
        Whitespace in the HTML obtained is a pain when scanning for next_sibling
        Clean up
    """
    html_text = re.sub(">\s*", ">", html_text)
    html_text = re.sub("\s*<", "<", html_text)
    return html_text


# init elasticsearch
# es = Elasticsearch(['localhost:9200'])
# Create index for the day. 400 is an exception if index already exists.
# es.indices.create(index=INDEX_NAME, ignore=400)

for stop in STOP_IDS:
    json_string = parse_html(stop)
    print(json_string)
    print('===========================================')

    #   es.create(index=INDEX_NAME, body=json_string)
    time.sleep(1)
