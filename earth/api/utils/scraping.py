import json
import requests
import logging
from bs4 import BeautifulSoup
from html import unescape
from sys import getsizeof
from time import sleep
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


class ScrapingMixin(object):
    SILENCE_EXCEPTIONS = (requests.ReadTimeout, requests.HTTPError, requests.ConnectTimeout)


    @classmethod
    def get_data(cls, url, timeout=10, headers=None, fail_silently=False):
        allowed_exceptions = cls.SILENCE_EXCEPTIONS if fail_silently else ()
        content = None
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            content = response.content
        except allowed_exceptions:
            pass

        return content

    @classmethod
    def get(self, url=None, as_json=True, **kwargs):
        response = self.get_data(url, **kwargs)
        if type(response) is bytes:
            response = response.decode('utf-8', 'ignore')
        if as_json:
            response = json.loads(response)

        return response

    @classmethod
    def add_query_params(self, url, **kwargs):
        parsed_url = urlparse(url)
        query_parameters = parse_qs(parsed_url.query)
        for key, value in kwargs.items():
            query_parameters[key] = [value]

        url = urlunparse(parsed_url._replace(query=urlencode(query_parameters, doseq=True)))
        return url


import re
class GetLatLong(object):
    """
    Wikipedia
    """
    import re
    KWARGS = [
        'List_of_',
        'wiki/Category:',
        'wiki/Wikipedia:'
    ]

    def dms2dd(self, degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
        if direction == 'E' or direction == 'N':
            dd *= -1
        return dd;

    def dd2dms(self, deg):
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60
        return [d, m, sd]

    def parse_dms(self, dms):
        parts = re.split('[^\d\w.]+', dms)
        lat = self.dms2dd(parts[0], parts[1], parts[2], parts[3])
        return (lat)

    def get_latitude_long_from_wikipedia_url(self, url):
        content = ScrapingMixin.get(url, as_json=False)
        soup = BeautifulSoup(content)
        latitude = soup.find_all('span', {'class': 'latitude'})[0]
        longitude = soup.find_all('span', {'class': 'longitude'})[0]
        values = (
            self.parse_dms(latitude.text),
            self.parse_dms(longitude.text)
        )
        return values

class StateParks(object):
    link = 'https://en.wikipedia.org/wiki/Lists_of_state_parks_by_U.S._state'
    links = [
        'https://en.wikipedia.org/wiki/List_of_Alabama_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Alaska_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Arizona_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Arkansas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_California_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Colorado_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Connecticut_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Delaware_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Florida_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Georgia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Hawaii_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Idaho_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Illinois_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Indiana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Iowa_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Kansas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Kentucky_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Louisiana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Maine_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Maryland_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Massachusetts_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Michigan_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Minnesota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Mississippi_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Missouri_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Montana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Nebraska_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Nevada_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Hampshire_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Jersey_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Mexico_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_York_state_parks',
        'https://en.wikipedia.org/wiki/List_of_North_Carolina_state_parks',
        'https://en.wikipedia.org/wiki/List_of_North_Dakota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Ohio_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Oklahoma_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Oregon_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Pennsylvania_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Rhode_Island_state_parks',
        'https://en.wikipedia.org/wiki/List_of_South_Carolina_state_parks',
        'https://en.wikipedia.org/wiki/List_of_South_Dakota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Tennessee_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Texas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Utah_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Vermont_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Virginia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Washington_state_parks',
        'https://en.wikipedia.org/wiki/List_of_West_Virginia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Wisconsin_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Wyoming_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Alabama_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Alaska_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Arizona_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Arkansas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_California_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Colorado_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Connecticut_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Delaware_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Florida_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Georgia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Hawaii_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Idaho_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Illinois_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Indiana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Iowa_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Kansas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Kentucky_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Louisiana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Maine_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Maryland_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Massachusetts_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Michigan_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Minnesota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Mississippi_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Missouri_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Montana_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Nebraska_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Nevada_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Hampshire_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Jersey_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_Mexico_state_parks',
        'https://en.wikipedia.org/wiki/List_of_New_York_state_parks',
        'https://en.wikipedia.org/wiki/List_of_North_Carolina_state_parks',
        'https://en.wikipedia.org/wiki/List_of_North_Dakota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Ohio_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Oklahoma_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Oregon_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Pennsylvania_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Rhode_Island_state_parks',
        'https://en.wikipedia.org/wiki/List_of_South_Carolina_state_parks',
        'https://en.wikipedia.org/wiki/List_of_South_Dakota_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Tennessee_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Texas_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Utah_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Vermont_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Virginia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Washington_state_parks',
        'https://en.wikipedia.org/wiki/List_of_West_Virginia_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Wisconsin_state_parks',
        'https://en.wikipedia.org/wiki/List_of_Wyoming_state_parks'
    ]
    STATES = {
         'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
         'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
         'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana',
         'Maine' 'Maryland','Massachusetts','Michigan','Minnesota',
         'Mississippi', 'Missouri','Montana','Nebraska','Nevada',
         'New Hampshire','New Jersey','New Mexico','New York',
         'North Carolina','North Dakota','Ohio',
         'Oklahoma','Oregon','Pennsylvania','Rhode Island',
         'South  Carolina','South Dakota','Tennessee','Texas','Utah',
         'Vermont','Virginia','Washington','West Virginia',
         'Wisconsin','Wyoming'
    }

    def get_all_urls(self):
        content = ScrapingMixin.get(self.link, as_json=False)
        soup = BeautifulSoup(content)
        links = [l for l in soup.find_all('a')]
        return links

    def for_link_in_all_links(self):
        from api.models import Location
        from urllib.parse import urlparse
        for link in self.links:
            content = ScrapingMixin.get(link, as_json=False)
            soup = BeautifulSoup(content)
            better = soup.find('div', {'class': 'mw-parser-output'})
            if not better:
                import ipdb
                ipdb.set_trace()

            lists = better.find_all('li')
            anchors = []
            for list in lists:
                anchor = [l for l in list.children if l != '\n'
                          and hasattr(l, 'attrs') and l.attrs.get('href')]
                anchors.extend(anchor)

            for a in anchors:
                link = a.attrs.get('href')
                parsed = urlparse(link)
                if not parsed.netloc:
                    link = 'https://en.wikipedia.org' + link
                name = a.attrs.get('title')
                if not name:
                    continue
                l = Location.objects.create(name=a.attrs.get('title'),
                                        link=link)
                print('created', l.name)

