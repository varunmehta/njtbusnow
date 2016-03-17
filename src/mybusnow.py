'''
The information we need to fetch out of this page.


Selected Route: 308
Selected Direction: Newark and New Y
Selected Stop: PROSPECT ST + WOODVALE RD
Selected Stop Number: 12067
Current Date: Mar 16, 2016 (EST) - # get in iso format
Current Time: 5:19 PM
Bus Route Name: To 164 NEW YORK
Bus Route Number: #164
Bus Number (Bus 7741)
ETA: 19 MIN
'''

import re
from bs4 import BeautifulSoup, NavigableString

# http://mybusnow.njtransit.com/bustime/wireless/html/eta.jsp?route=---&direction=---&displaydirection=---&stop=---&id=12067
BASE_URL = 'http://mybusnow.njtransit.com/bustime/wireless/html/eta.jsp'


def strip_html_whitespace(html_text):
    """
        Whitespace in the HTML obtained is a pain when scanning for next_sibling
        Clean up
    """
    html_text = re.sub(">\s*", ">", html_text)
    html_text = re.sub("\s*<", "<", html_text)
    return html_text


def parse_html():
    # html_page = requests.get(BASE_URL)
    html_page = open("../test/eta.html", "r")
    html_text = html_page.read()
    html_text = strip_html_whitespace(html_text)
    soup = BeautifulSoup(html_text, "lxml")

    # First parse all the bus related information.
    ps = soup.find_all('p', limit=3)
    parse_rt_info(ps)

    # <hr/> works as line seperators between buses, so that can be used to demarcate buses.
    hrs = soup.find_all('hr')
    parse_bus(hrs)
    print('===========================================')


def parse_rt_info(ps):
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

        if count == 1:
            count += 1
            currently = p.next_element
            print(currently)
            continue

        if count == 2:
            count += 1

            rt = p.next_element
            print(rt)
            direction = rt.next_sibling.next_element
            print(direction)
            stop = direction.next_sibling.next_element
            print(stop)
            stop_no = stop.next_sibling.next_element
            print(stop_no)

        print('xxxxxxxxxxxx')


def parse_bus(hrs):
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

        bus_rt_no = hr.next_sibling
        print(bus_rt_no.text)
        bus_rt_name = bus_rt_no.next_sibling
        print(bus_rt_name)
        bus_eta = bus_rt_name.next_sibling
        print(bus_eta.text)
        bus_no = bus_eta.next_sibling.next_sibling.text
        print(bus_no)
        print('~~~~~~~~~~~~~~~~~~~')
        count += 1


parse_html()
