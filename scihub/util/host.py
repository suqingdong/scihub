import re

from dateutil.parser import parse as date_parse
from webrequests import WebRequest as WR


def check_host():
    """
        checking available urls of Sci-Hub
    """
    url = 'https://lovescihub.wordpress.com/'

    soup = WR.get_soup(url)

    text = soup.select_one('.entry-content p:nth-child(2)').text
    update_text = soup.select_one('.entry-title').text
    update_time = date_parse(re.findall(r'Last check time:(.+?)\)', update_text)[0])

    hosts = dict(re.findall(r'(http.+?)\s+(.+?s)', text))

    return hosts, update_time


if __name__ == "__main__":
    from pprint import pprint
    hosts, update_time = check_host()
    print(update_time)
    pprint(hosts)

"""
Other URL: https://gfsoso.99lb.net/sci-hub.html
- https://sci-hub.ren
- https://sci-hub.tf
"""
