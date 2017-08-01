from os import urandom
from hashlib import sha1
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
    cleaned = models.BooleanField(default=False)

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

    def clean(self, commit=False):
        required_fields = ('permalink', 'base64_encoded_image',
                           'title', 'preview_image_url')
        for field in required_fields:
            value = getattr(self, field)
            if not len(value):
                raise ValueError('%s has no value!' % field)

        self.cleaned = True
        if commit:
            self.save(update_fields=['cleaned'])


class QuerySetting(models.Model):
    OPERANDS = (
        ('ge', 'Greater than'),
        ('le', 'Less than')
    )

    url_identifier = models.CharField(max_length=255)
    query_keywords_title = models.TextField(null=True)
    score_threshold_operand = models.CharField(choices=OPERANDS)
    score_threshold = models.IntegerField(null=True)


    def get_identifier(self):
        """
        creates unique identifier to be used in URL
        """
        return str(sha1(urandom(6)).hexdigest())[:5]

