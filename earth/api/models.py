from os import urandom
from hashlib import sha1
from django.db import models


class EarthManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()\
            .filter(score__gte=20)\
            .filter(is_public=True)


class EarthImage(models.Model):
    # fields
    permalink = models.URLField()
    image_url = models.URLField()
    preview_image_url = models.URLField()
    preferred_image_url = models.URLField(default='')
    original_source = models.BooleanField(default=False)
    title = models.CharField(max_length=500)
    raw_title = models.CharField(max_length=500, default='')
    author = models.CharField(max_length=255)
    subreddit_name = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    created_raw = models.CharField(max_length=255)
    cleaned = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    resolution_width = models.IntegerField(null=True)
    resolution_height = models.IntegerField(null=True)
    last_seen = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    public = EarthManager()

    @classmethod
    def create(cls, data):
        image_obj = cls(
            permalink=data.get('permalink'),
            image_url=data.get('url'),
            raw_title=data.get('title'),
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

        title_string = ''.join(cleaned_title)
        DISALLOWED_KEYWORDS = ('OC', 'oc', '(OC)')
        for disallowed_word in DISALLOWED_KEYWORDS:
            title_string = title_string.replace(disallowed_word, '')

        return title_string.strip()


    def clean(self, commit=False):
        required_fields = ('permalink', 'title', 'preferred_image_url')
        for field in required_fields:
            value = getattr(self, field)
            if not len(value):
                raise ValueError('%s has no value!' % field)

        if not self.image_url and not self.preview_image_url:
            raise ValueError('Must specify either image_url or preview_url')

        self.cleaned = True
        if commit:
            self.save(update_fields=['cleaned'])

    def update_seen(self):
        self.save(update_fields=['last_seen'])

    def update_raw_title(self, post_data):
        if post_data is not None:
            self.raw_title = post_data.get('title', '')
            if self.raw_title:
                self.set_public()

    def set_public(self):
        """
        based on certain quality inspections, make public or not
        """
        RESOLUTION_THRESHOLD_WIDTH = 1200
        # resolution from title
        for word in self.raw_title.split():
            if 'x' not in word:
                continue

            try:
                width, height = [''.join(c for c in w if c.isdigit())
                                 for w in word.split('x')]
                self.resolution_width = int(width)
                self.resolution_height = int(height)
            except ValueError:
                continue

        if self.resolution_width is not None and self.resolution_width < RESOLUTION_THRESHOLD_WIDTH:
            self.is_public = False

        try:
            self.clean()
        except ValueError:
            self.is_public = False

        self.save()



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
    WIDTH = 'width'
    HEIGHT = 'height'
    RESOLUTIONS = (
        (WIDTH, 'Width'),
        (HEIGHT, 'Height')
    )

    url_identifier = models.CharField(max_length=255)
    query_keywords_title = models.TextField(null=True, blank=True)
    score_type = models.CharField(max_length=100, choices=TYPES, default=SCORE)
    score_threshold_operand = models.CharField(choices=OPERANDS, max_length=5, default='gte')
    score_threshold = models.IntegerField(null=True, blank=True)
    resolution_type = models.CharField(choices=RESOLUTIONS, default=WIDTH, max_length=8)
    resolution_threshold_operand = models.CharField(choices=OPERANDS, default='gte', max_length=8)
    resolution_threshold = models.IntegerField(null=True, blank=True)

    @classmethod
    def get_identifier(cls):
        """
        creates unique identifier to be used in URL
        """
        return str(sha1(urandom(6)).hexdigest())[:5]

