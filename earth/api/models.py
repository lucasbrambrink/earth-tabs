from django.db import models


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
    created_raw = models.CharField(max_length=255)

    @classmethod
    def create(cls, data):
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
            created_raw=str(data.get('created_utc'))
        )
        return image_obj


