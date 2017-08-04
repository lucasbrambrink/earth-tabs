import json
import requests
import logging
from bs4 import BeautifulSoup
from html import unescape
from sys import getsizeof
from time import sleep
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


logger = logging.getLogger(__name__)


class EarthScraper(object):
    DEFAULT_SUBREDDIT = 'EarthPorn'
    REDDIT_URL = 'https://www.reddit.com/'
    JSON_SUFFIX = '.json'
    SEARCH = 'search?q=nepal&restrict_sr=on&sort=relevance&t=all'

    DISALLOWED_LINKS = {
        'http://i.imgur.com/removed.png'
    }
    ALL = 'all'
    YEAR = 'year'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'
    TIME_FRAMES = (ALL, YEAR, MONTH, WEEK, DAY)

    def get_url(self, after_address=None, subreddit=None, sort_top=False, time_frame=None, search_param=None):
        subreddit = subreddit or self.DEFAULT_SUBREDDIT
        path = [self.REDDIT_URL, 'r', subreddit]

        add_query_params = {}
        if after_address is not None:
            add_query_params['after'] = after_address

        if search_param is not None:
            sort_top = False
            path.append('search')
            add_query_params['q'] = search_param
            add_query_params['restrict_sr'] = 'on'
            add_query_params['sort'] = 'relevance'
            add_query_params['t'] = time_frame

        if sort_top:
            path.append('top')
            add_query_params['sort'] = 'top'
            if time_frame is None or time_frame not in self.TIME_FRAMES:
                time_frame = self.ALL
            add_query_params['t'] = time_frame

        path.append(self.JSON_SUFFIX)
        base_path = '/'.join(path)
        url = self.add_query_params(base_path, **add_query_params)
        return url

    def get_data(self, url, timeout=10):
        response = requests.get(url, headers={'User-agent': 'Earth images bot 1.0'}, timeout=timeout)
        response.raise_for_status()
        return response.content

    def get(self, url=None, **kwargs):
        url = url or self.get_url(**kwargs)
        response = self.get_data(url)
        if type(response) is bytes:
            response = response.decode('utf-8', 'ignore')
        content = json.loads(response)
        return content.get('data', {})

    def add_query_params(self, url, **kwargs):
        parsed_url = urlparse(url)
        query_parameters = parse_qs(parsed_url.query)
        for key, value in kwargs.items():
            query_parameters[key] = [value]

        url = urlunparse(parsed_url._replace(query=urlencode(query_parameters, doseq=True)))
        return url

    def get_image_urls(self, data):
        image_url = data.get('url')
        image_url = self.clean_imgur_link(image_url)

        image = None
        if image_url is not None and image_url not in self.DISALLOWED_LINKS:
            try:
                image = self.get_data(image_url, timeout=1)
            except (requests.HTTPError, requests.ReadTimeout):
                pass

        # get reddit hosted preview image URL
        # fetch largest of them based on width
        preview_images = data\
            .get('preview', {})\
            .get('images', [{}])[0]\
            .get('resolutions', {})

        if not len(preview_images):
            return '', image_url

        best_image = max(preview_images, key=lambda i: i.get('width'))
        preview_image_url = unescape(best_image.get('url'))

        if image is None:
            preferred_image_url = preview_image_url
        else:
            preview_image = self.get_data(preview_image_url)
            # allow HTTP error here; i.reddit links should always work

            # compare which one is higher resolution (by sheer bytes)
            preferred_image_url = preview_image_url if \
                getsizeof(image) < getsizeof(preview_image) \
                    else image_url

        return preview_image_url, preferred_image_url

    def clean_imgur_link(self, url):
        IMGUR_DOMAIN = 'imgur.com'
        if not IMGUR_DOMAIN in url:
            return url

        parsed_url = urlparse(url)
        # might already be a direct link
        DIRECT_LINK_DOMAIN = 'i.imgur.com'
        if parsed_url.netloc == DIRECT_LINK_DOMAIN:
            return url

        # if not direct link, try to get it from HTML
        direct_link = None
        try:
            image_html = self.get_data(url)
            soup = BeautifulSoup(image_html,'html.parser')
            direct_link = soup\
                .find('div', attrs={'class': 'post-image'})\
                .find('a').attrs.get('href')
        except (requests.ReadTimeout,
                requests.HTTPError,
                requests.ConnectTimeout,
                ValueError,
                AttributeError):
            pass

        if direct_link is not None:
            parsed_direct_link = urlparse(direct_link)
            if parsed_direct_link.scheme == '':
                parsed_direct_link = parsed_direct_link._replace(scheme='https')

            direct_link = urlunparse(parsed_direct_link)

        return direct_link

    def get_post_data_from_permalink(self, permalink):
        url = '{base}{permalink}{json}'.format(
            base=self.REDDIT_URL, permalink=urlparse(permalink).path[1:], json=self.JSON_SUFFIX)
        try:
            response = self.get_data(url=url)
            if type(response) is bytes:
                response = response.decode('utf-8', 'ignore')
            content = json.loads(response)
        except Exception as exc:
            logger.warning('Unable to load %s' % url)
            logger.warning(exc)
            content = []

        data = None
        try:
            data = content[0]['data']['children'][0]['data']
        except (IndexError, KeyError):
            pass

        return data

    def update_existing_instances(self):
        from .models import EarthImage
        for instance in EarthImage.objects.filter(raw_title=''):
            post_data = self.get_post_data_from_permalink(instance.permalink)
            instance.update_raw_title(post_data)
            instance.set_public()
            logger.info('Updated %s' % instance.title)
            sleep(0.5)

    def batch_import(self, limit_new=25, continue_batch=None, after_address=None, sort_top=False, time_frame=None, search_param=None):
        from .models import EarthImage

        images_to_be_added = continue_batch or []
        seen_urls = {i.permalink for i in images_to_be_added}

        while len(images_to_be_added) < limit_new:
            data = self.get(after_address=after_address,
                            sort_top=sort_top, time_frame=time_frame, search_param=search_param)
            after_address = data.get('after')
            posts = data.get('children')
            for post in posts:
                post_data = post.get('data')
                preview, preferred = self.get_image_urls(post_data)
                image_obj = EarthImage.create(post_data)
                image_obj.preview_image_url = preview
                image_obj.preferred_image_url = preferred
                image_obj.original_source = preferred == image_obj.image_url

                if image_obj.permalink in seen_urls:
                    continue

                seen_urls.add(image_obj.permalink)
                images_to_be_added.append(image_obj)

            # throttle request speed a little bit
            sleep(5)

        # fetch posts that already exist (1 SQL query)
        urls = [obj.permalink for obj in images_to_be_added]
        duplicates = set(EarthImage.objects\
            .filter(permalink__in=urls)\
            .values_list('permalink', flat=True))
        # filter by existence
        images_to_be_added = [obj for obj in images_to_be_added
                              if obj.permalink not in duplicates]

        # keep adding to it until we have enough that don't filter
        if len(images_to_be_added) < limit_new:
            return self.batch_import(limit_new=limit_new,
                                     continue_batch=images_to_be_added,
                                     after_address=after_address,
                                     sort_top=sort_top, time_frame=time_frame)

        EarthImage.objects.bulk_create(images_to_be_added[:limit_new])
