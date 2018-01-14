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