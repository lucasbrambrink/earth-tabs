import json
import requests
import base64

from .models import EarthImage


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
        content = json.loads(self.get_data(url))
        return content.get('data', {}).get('children')

    def get_image_data(self, image_url):
        image = self.get_data(image_url)
        return base64.b64encode(image)

    def get_preview_image(self, data):
        # get image data from preview object?
        preview_images = data.get('preview', {}).get('images', [{}])[0].get('resolutions')
        best_image = max(preview_images, key=lambda i: i.get('width'))
        return best_image.get('url')

    def batch_import(self, limit_new=25):
        images_to_be_added = []
        for page_num in range(1, 100):
            posts = self.get(page_num=page_num)

            for post in posts:
                image_url = self.get_preview_image(post)
                img_data = self.get_image_data(image_url)
                image_obj = EarthImage.create(post)
                image_obj.preview_image_url = image_url
                image_obj.base64_encoded_image = img_data

                try:
                    # skip posts that already exist
                    EarthImage.objects.get(permalink=image_obj.permalink)
                except EarthImage.DoesNotExist:
                    images_to_be_added.append(image_obj)

            if len(images_to_be_added) > limit_new:
                break

        EarthImage.objects.bulk_create(images_to_be_added[:limit_new])
