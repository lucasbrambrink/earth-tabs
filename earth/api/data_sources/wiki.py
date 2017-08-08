import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from api.utils.scraping import ScrapingMixin
import datetime
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

        links = []
        for section in soup.findAll('table',
                attrs={'role': 'presentation', 'class': ''}):
            tag = section.find('a', attrs={'class': 'image'})
            if tag is None:
                continue
            image = {
                'title': tag.attrs.get('title', 'Not found')[:500],
                'image_url': tag.attrs.get('href', ''),
                'preview_image_url': url,
            }
            links.append(image)

        titles = [t.text for t in soup.findAll('span',
            attrs={'class': 'mw-headline'})]

        for title, link in zip(titles, links):
            link['created_raw'] = title[:200]

        # get the coveted original file link
        for link in links:
            url = '{base}/wiki/File:{file}'.format(
                base=self.BASE_URL,
                file=link['image_url'].split('File:')[1])
            picture_page_html = self.get(url, as_json=False, headers=self.HEADERS)
            psoup = BeautifulSoup(picture_page_html, 'html.parser')
            og_link = [a for a in psoup.findAll('a', attrs={'class': 'internal'})
                       if 'Original file' in a.text]
            if not len(og_link):
                continue
            href = og_link[0].attrs.get('href', '')
            parsed_url = urlparse(href)
            parsed_url = parsed_url._replace(scheme='https')
            link['preferred_image_url'] = urlunparse(parsed_url)

        return links

    def create_models(self, links):
        from api.models import EarthImage
        PERMALINK = '/wiki/Template:POTD/'
        # objects = []
        for link in links:
            obj = EarthImage(**link)
            obj.source = 'wiki'
            obj.is_public = True
            obj.score = 20
year_month = obj.preview_image_url.split('/')[-1]
year = year_month.split('_')[1]
date_string = '{}{}'.format(obj.created_raw.split('-')[0], year)
date = datetime.datetime.strptime(date_string, '%B %d %Y')
            obj.permalink = '{base}{path}{time}'.format(
                base=self.BASE_URL,
                path=PERMALINK,
                time=date.strftime('%Y-%m-%d')
            )
            obj.author = 'Wikipedia: {}'.format(date.strftime('%B %d, %Y'))
            # objects.append(obj)
            try:
                obj.save()
            except Exception as exc:
                logger.warning(exc)

        # EarthImage.objects.bulk_create(objects)


    def fetch_year(self, year):
        months = [datetime.date(year, month, 1)
                  for month in range(1, 13)]
        urls = ['{base}{path}/{time}'.format(
            base=self.BASE_URL,
            path=self.PATH,
            time=month.strftime('%B_%Y')
        ) for month in months]
        for url in urls:
            self.run(url)
        return urls

    def run(self, url):
        links = self.scrape_wiki(url)
        self.create_models(links)

