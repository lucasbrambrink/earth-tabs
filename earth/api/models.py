from os import urandom
from hashlib import sha1
from django.db import models


class EarthImage(models.Model):
    # fields
    permalink = models.URLField()
    image_url = models.URLField()
    preview_image_url = models.URLField()
    preferred_image_url = models.URLField(default='')
    original_source = models.BooleanField(default=False)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255)
    subreddit_name = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    created_raw = models.CharField(max_length=255)
    cleaned = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, data):
        image_obj = cls(
            permalink=data.get('permalink'),
            image_url=data.get('url'),
            title=cls.clean_title(data.get('title')),
            author=data.get('author'),
            subreddit_name=data.get('subreddit'),
            score=data.get('score', 0),
            ups=data.get('ups', 0),
            downs=data.get('downs', 0),
            num_comments=data.get('num_comments', 0),
            created_raw=str(data.get('created_utc'))
        )
        return image_obj

    @classmethod
    def clean_title(cls, title):
        cleaned_title = []
        characters = (c for c in title)
        is_open = False
        for c in characters:
            if c == '[':
                is_open = True
                continue
            elif c == ']':
                is_open = False
                continue

            if not is_open:
                cleaned_title.append(c)

        return ''.join(cleaned_title)


    def clean(self, commit=False):
        required_fields = ('permalink',  # 'base64_encoded_image',
                           'title', 'preview_image_url')
        for field in required_fields:
            value = getattr(self, field)
            if not len(value):
                raise ValueError('%s has no value!' % field)

        self.cleaned = True
        if commit:
            self.save(update_fields=['cleaned'])

    def update_seen(self):
        self.save(update_fields=['last_seen'])


class QuerySetting(models.Model):
    OPERANDS = (
        ('gte', 'Greater than'),
        ('lte', 'Less than')
    )
    SCORE = 'score'
    DOWNVOTE = 'downs'
    UPVOTE = 'ups'
    TYPES = (
        (SCORE, 'Score'),
        (DOWNVOTE, 'Downvotes'),
        (UPVOTE, 'Upvotes')
    )

    url_identifier = models.CharField(max_length=255)
    query_keywords_title = models.TextField(null=True, blank=True)
    score_type = models.CharField(max_length=100, choices=TYPES, default=SCORE)
    score_threshold_operand = models.CharField(choices=OPERANDS, max_length=5, default='gte')
    score_threshold = models.IntegerField(null=True, blank=True)

    @classmethod
    def get_identifier(cls):
        """
        creates unique identifier to be used in URL
        """
        return str(sha1(urandom(6)).hexdigest())[:5]

