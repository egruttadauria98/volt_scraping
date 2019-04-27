import mechanize
from http.cookiejar import CookieJar, Cookie
import ssl
from bs4 import BeautifulSoup
import pandas as pd
import re

from login import get_login_data

br = mechanize.Browser()
cj = CookieJar()

login_url, cookie_val = get_login_data()

def volt_login():

    cj.set_cookie(Cookie(name="_community_hr_session", value=cookie_val,
                         port=None, port_specified=False,
                         domain='volt.team',
                         domain_specified=False,
                         domain_initial_dot=False, path='/',
                         secure=False, expires=None, discard=True,
                         comment=None, rest={'HttpOnly': None},
                         rfc2109=False, comment_url=None,
                         path_specified=False, version=0))


    br.set_cookiejar(cj)


    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)

    br.addheaders = [('User-agent', 'Firefox')]

    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.set_ca_data(context=ssl._create_unverified_context(cert_reqs=ssl.CERT_NONE))


    # LOGIN

    br.open(login_url)
    #Choose form
    br.form = list(br.forms())[0]

    #Set value for "Email"
    br["Email"] = "XXX"
    br.submit()
    br.response().read()
    #Set "Passwd"
    br.form = list(br.forms())[0]
    br["Passwd"] = "XXX"
    br.submit()

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    string = re.sub(clean, '', str(text))
    return string

def num_pages(soup):

    num_people = int(remove_html_tags(soup.find('p')).split()[1])
    people_per_page = 25
    num_pages = (num_people//people_per_page) + 1
    return num_pages

def get_profile_data(profile_link):

    '''
    BISOGNA AGGIUNGERE INFO SU TEAMS E POSIZIONI
    '''

    cols = dict()

    br.open(profile_link)
    soup = BeautifulSoup(br.response().read(), features="html5lib")

    table_tag = soup.find_all("table", class_="no-border no-strip skills")

    lines_1 = table_tag[0].find("tbody").find_all("tr")

    for line in lines_1:
        values = line.find_all('td')
        cols[remove_html_tags(values[1])] = remove_html_tags(values[2])

    lines_2 = table_tag[1].find("tbody").find_all("tr")

    for line in lines_2:
        values = line.find_all('td')
        cols[remove_html_tags(values[0])] = remove_html_tags(values[1])

    return cols

def single_table(soup, k):

    table_tag = soup.find("table", class_="table table-striped table-hover")
    cols = table_tag.find_all("th")

    cols = [remove_html_tags(col) for col in cols]

    table_dict = dict()
    all_profile_dict = dict()

    for col in cols:
        table_dict[col] = []

    lines = soup.find("tbody").find_all("tr")

    for line in lines:
        values = line.find_all('td')
        profile_href = line.find('a', href=True)
        profile_url = 'https://volt.team' + remove_html_tags(profile_href['href'])

        profile_dict = get_profile_data(profile_url)

        for key, value in zip(profile_dict.keys(), profile_dict.values()):

            try:
                value = remove_html_tags(value).rstrip().strip()
                all_profile_dict[key].append(value)
            except:
                all_profile_dict[key] = []
                all_profile_dict[key].append(value)

        for key, value in zip(table_dict.keys(), values):

            value = remove_html_tags(value).rstrip().strip()
            table_dict[key].append(value)

    try:

        # DUPLICATED FIELDS OVERWRITTEN?

        complete_dict = {**table_dict, **all_profile_dict}
        table = pd.DataFrame(complete_dict, columns=complete_dict.keys())

        if k==0:
            val = 'New'
        elif k==1:
            val = 'Pending activation'
        elif k==2:
            val = 'Active'
        elif k==3:
            val = 'Inactive'

        table['Type'] = val

        return table

    except:
        pass


def create_table(url_table, filter):

    start_url = 'https://volt.team/volunteers?country=IT&page=1&team_filter=' + filter

    urls = [
        url_table,
        url_table + "/pending",
        url_table + "/active",
        url_table + "/inactive"
    ]

    for k, url in enumerate(urls):

        filter_url = url + '?country=IT&page=1&team_filter=' + filter
        br.open(filter_url)
        soup = BeautifulSoup(br.response().read(), features="html5lib")
        pages = num_pages(soup)

        for i in range(pages):

            page_url = url + '?country=IT&page=' + str(i+1) + '&team_filter=' + filter

            br.open(page_url)
            print(br.geturl())

            soup = BeautifulSoup(br.response().read(), features="html5lib")

            table = single_table(soup, k)

            if page_url == start_url:
                complete_table = table
            else:
                complete_table = pd.concat([complete_table, table], ignore_index=True, sort=False)


    complete_table.drop([''], axis=1, inplace=True)
    complete_table.to_csv('/Users/eliogruttadauria/Desktop/a.csv')

volt_login()
url_table = "https://volt.team/volunteers"
create_table(url_table, 'all')
