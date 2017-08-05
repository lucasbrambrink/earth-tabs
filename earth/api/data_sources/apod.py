import datetime

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from api.utils.scraping import ScrapingMixin


class ApodScraper(ScrapingMixin,
                  object):

    APOD_BASE = 'https://apod.nasa.gov/apod/'
    TODAY = 'astropix.html'
    ARCHIVE = 'archivepix.html'
    HEADERS = {'User-agent': 'Earth images bot 1.0'}


    def scrape_apod(self, url=None):
        from api.models import EarthImage

        url = url or '{base}{today}'.format(base=self.APOD_BASE,
                                            today=self.TODAY)
        html = self.get(url, as_json=False, headers=self.HEADERS)
        soup = BeautifulSoup(html, 'html.parser')

        # scrape html elements
        image = soup.find('center').find('img')
        title = soup.findAll('center')[1].findAll('b')[0]
        created_raw = soup.find('center').findAll('p')[1]

        # format them a little
        image_url = '{base}{image_url}'.format(base=self.APOD_BASE,
                                               image_url=image.attrs.get('src'))
        raw_title = title.contents[0].strip()
        permalink = self.get_permalink(url)
        created_raw = created_raw.contents[0].strip()

        # commit to object
        obj = EarthImage(
            image_url=image_url,
            preferred_image_url=image_url,
            title=raw_title,
            raw_title=raw_title,
            created_raw=created_raw,
            permalink=permalink,
            source=EarthImage.APOD,
            score=100,
            author=created_raw
        )
        return obj

    def get_permalink_timestamp_for_date(self, date=None):
        date = date or datetime.date.today()
        return 'ap{date}.html'.format(date=date.strftime('%y%m%d'))

    def get_permalink(self, url):
        parsed_url = urlparse(url)
        path_components = parsed_url.path.split('/')
        if self.TODAY in path_components:
            path_components.remove(self.TODAY)
            path_components.append(self.get_permalink_timestamp_for_date())

        return urlunparse(parsed_url._replace(path='/'.join(path_components)))

    def batch_import(self, limit=25, start_at=None):
        from api.models import EarthImage

        if start_at is None:
            start_at = datetime.date.today()

        existing_image_links = set(EarthImage.objects
            .filter(source=EarthImage.APOD)
            .values_list('permalink', flat=True))

        images_to_be_added = []
        date_to_scrape = start_at
        while len(images_to_be_added) < limit:
            new_link = '{base}{uri}'.format(base=self.APOD_BASE,
                                            uri=self.get_permalink_timestamp_for_date(date_to_scrape))
            if new_link not in existing_image_links:
                try:
                    new_image = self.scrape_apod(new_link)
                except AttributeError:
                    new_image = None

                existing_image_links.add(new_link)
                if new_image is not None:
                    images_to_be_added.append(new_image)

            date_to_scrape = date_to_scrape - datetime.timedelta(days=1)

        EarthImage.objects.bulk_create(images_to_be_added[:limit])
