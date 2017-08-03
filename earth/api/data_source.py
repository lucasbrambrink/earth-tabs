import json
import requests
import base64
from html import unescape

class EarthScraper(object):
    DEFAULT_SUBREDDIT = 'EarthPorn'
    REDDIT_URL = 'https://www.reddit.com/r/{subreddit}/.json'

    def get_url(self, page_num=1, subreddit=None):
        subreddit = subreddit or self.DEFAULT_SUBREDDIT
        base_url = self.REDDIT_URL.format(subreddit=subreddit)
        return '{base_url}?page={page_num}'.format(
            base_url=base_url,
            page_num=page_num
        )

    def get_data(self, url):
        response = requests.get(url, headers = {'User-agent': 'Earth images bot 1.0'})
        response.raise_for_status()
        return response.content

    def get(self, **kwargs):
        url = self.get_url(**kwargs)
        response = self.get_data(url)
        if type(response) is bytes:
            response = response.decode('utf-8', 'ignore')
        content = json.loads(response)
        return content.get('data', {}).get('children')

    def get_image_urls(self, data):
        image_url = data.get('url')
        try:
            image = self.get_data(image_url)
        except requests.HTTPError:
            image = None

        # get reddit hosted preview image URL
        # fetch largest of them based on width
        preview_images = data.get('preview', {}).get('images', [{}])[0].get('resolutions', {})
        best_image = max(preview_images, key=lambda i: i.get('width'))
        preview_image_url = unescape(best_image.get('url'))

        preferred_image_url = None
        if image is None:
            preview_image_url = preview_image_url
        else:
            preview_image = self.get_data(preview_image_url)
            # allow HTTP error here!

            # compare which one is higher resolution (by sheer bytes)
            preferred_image_url = preview_image_url if \
                len(base64.b64encode(image)) < len(base64.b64encode(preview_image)) \
                    else image_url

        return preview_image_url, preferred_image_url

    def batch_import(self, limit_new=25, continue_batch=None, page_number=1):
        from .models import EarthImage

        images_to_be_added = continue_batch or []
        seen_urls = {i.permalink for i in images_to_be_added}

        current_page_num = page_number
        while len(images_to_be_added) < limit_new:
            posts = self.get(page_num=current_page_num)
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

            current_page_num += 1

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
                                     page_number=current_page_num)

        EarthImage.objects.bulk_create(images_to_be_added[:limit_new])
