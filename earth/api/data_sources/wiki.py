import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from api.utils.scraping import ScrapingMixin

logger = logging.getLogger(__name__)


class WikiScraper(ScrapingMixin,
                               object):
    BASE_URL = 'https://en.wikipedia.org'
    PATH = '/wiki/Wikipedia:Picture_of_the_day'
    HEADERS = {'User-agent': 'Earth images bot 1.0'}
    ALLOWED_FORMATS = ('.jpg', '.png')

    def scrape_wiki(self, url):
        html = self.get(url, as_json=False, headers=self.HEADERS)
        soup = BeautifulSoup(html, 'html.parser')


        all_tags = [a for a in soup.findAll('a')
                    if self.PATH in a.attrs.get('href', '')]





        import ipdb; ipdb.set_trace()
