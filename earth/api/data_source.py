import json
import requests
from sys import getsizeof

from html import unescape

class EarthScraper(object):
    DEFAULT_SUBREDDIT = 'EarthPorn'
    REDDIT_URL = 'https://www.reddit.com/r/{subreddit}/.json'

    DISALLOWED_LINKS = {
        'http://i.imgur.com/removed.png'
    }

    def get_url(self, after_address=None, subreddit=None):
        subreddit = subreddit or self.DEFAULT_SUBREDDIT
        url = self.REDDIT_URL.format(subreddit=subreddit)
        if after_address is not None:
            url = '{url}?after={address}'.format(url=url, address=after_address)
        return url

    def get_data(self, url, timeout=10):
        response = requests.get(url, headers={'User-agent': 'Earth images bot 1.0'}, timeout=timeout)
        response.raise_for_status()
        return response.content

    def get(self, **kwargs):
        url = self.get_url(**kwargs)
        response = self.get_data(url)
        if type(response) is bytes:
            response = response.decode('utf-8', 'ignore')
        content = json.loads(response)
        return content.get('data', {})

    def get_image_urls(self, data):
        image_url = data.get('url')
        try:
            image = self.get_data(image_url, timeout=1)
        except (requests.HTTPError, requests.ReadTimeout):
            image = None

        # get reddit hosted preview image URL
        # fetch largest of them based on width
        preview_images = data\
            .get('preview', {})\
            .get('images', [{}])[0]\
            .get('resolutions', {})
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

    def batch_import(self, limit_new=25, continue_batch=None, after_address=None):
        from .models import EarthImage

        images_to_be_added = continue_batch or []
        seen_urls = {i.permalink for i in images_to_be_added}

        while len(images_to_be_added) < limit_new:
            data = self.get(after_address=after_address)
            after_address = data.get('after')
            posts = data.get('children')
            for post in posts:
                post_data = post.get('data')
                preview, preferred = self.get_image_urls(post_data)
                image_obj = EarthImage.create(post_data)
                image_obj.preview_image_url = preview
                image_obj.preferred_image_url = preferred

                if image_obj.permalink in seen_urls:
                    continue

                seen_urls.add(image_obj.permalink)
                images_to_be_added.append(image_obj)

            # import ipdb; ipdb.set_trace()
            # sleep(10)

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
            return self.batch_import(continue_batch=images_to_be_added,
                                     after_address=after_address)

        EarthImage.objects.bulk_create(images_to_be_added[:limit_new])
