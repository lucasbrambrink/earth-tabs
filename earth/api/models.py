import base64
from django.db import models
from .data_source import EarthScraper


class EarthImage(models.Model):
    # fields
    permalink = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)
    preview_image_url = models.CharField(max_length=255)
    base64_encoded_image = models.TextField(null=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    subreddit_name = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    created_raw = models.DateField(max_length=255)

    @classmethod
    def create(cls, post_data):
        data = post_data.get('data')

        image_obj = cls(
            permalink=data.get('permalink'),
            image_url=data.get('url'),
            title=data.get('title'),
            author=data.get('author'),
            subreddit_name=data.get('subreddit'),
            score=data.get('score', 0),
            ups=data.get('ups', 0),
            downs=data.get('downs', 0),
            num_comments=data.get('num_comments', 0),
            created_raw=data.get('created_utc')
        )
        # get image data from preview object?
        preview_images = data.get('preview', {}).get('images', [{}])[0].get('resolutions')
        best_image = max(preview_images, key=lambda i: i.get('width'))
        best_preview_url = best_image.get('url')
        image_obj.preview_image_url = best_preview_url
        image_obj.base64_encoded_image = cls.get_image_data(best_preview_url)

        return image_obj


