from os import urandom
from hashlib import sha1
from django.db import models


from . import filters


class EarthManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()\
            .filter(score__gte=20)\
            .filter(is_public=True)

class MarketingManager(models.Manager):
    MARKETING_FILTER = filters.ScoreFilter(
        type=filters.Filter.GLOBAL,
        source='reddit',
        score_type='score',
        score_threshold_operand='gte',
        score_value=20000
    )

    def get_queryset(self):
        qs = super().get_queryset()\
            .filter(is_public=True)
        qs = self.MARKETING_FILTER.filter(qs)
        return qs


class EarthImage(models.Model):
    REDDIT = 'reddit'
    APOD = 'apod'
    WIKI = 'wiki'
    ALL = 'all'
    # WIKIPEDIA = 'wikipedia'
    VERIFIED_SOURCES = (
        (ALL, 'all'),
        (REDDIT, 'reddit.com/r/Earth'),
        (APOD, "NASA's Astronomy Picture of the Day"),
        (WIKI, 'Wikipedia Picture of the Day')
    )
    SOURCES = (REDDIT, APOD, WIKI)

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
    source = models.CharField(max_length=100, choices=VERIFIED_SOURCES, default=REDDIT)
    contain_image = False
    location = models.ForeignKey(to='Location', null=True,
                                 on_delete=models.SET_NULL)
    google_map_url = ''
    objects = models.Manager()
    public = EarthManager()
    marketing = MarketingManager()

    def __str__(self):
        return '{id}: {title}'.format(id=self.id, title=self.title)

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
        DISALLOWED_KEYWORDS = ('(OC)', 'OC', 'oc', '()')
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

    @classmethod
    def update_resolution(cls, query_set=None, limit=100):
        from api.utils.image import InspectImage
        if query_set is None:
            query_set = cls.objects\
                .filter(models.Q(resolution_width__isnull=True) |
                        models.Q(resolution_height__isnull=True))

        query_set = query_set[:limit]
        for image in query_set:
            InspectImage.inspect(image)


class Filter(models.Model):
    QUERY = 'query'
    RESOLUTION = 'resolution'
    SCORE = 'score'
    FILTER_TYPES = {
        QUERY: filters.TitleKeyWordFilter,
        RESOLUTION: filters.ResolutionFilter,
        SCORE: filters.ScoreFilter
    }
    CLASSES = (
        (QUERY, 'By keyword in title filter'),
        (RESOLUTION, 'Resolution filter'),
        (SCORE, 'Voting filter')
    )

    type = models.CharField(max_length=20, choices=filters.Filter.TYPES_CHOICES,
                            default=filters.Filter.GLOBAL)
    source = models.CharField(max_length=20, blank=True, default='', choices=EarthImage.VERIFIED_SOURCES)
    filter_class = models.CharField(max_length=10, choices=CLASSES)
    setting = models.ForeignKey(to='QuerySetting')
    arguments = models.CharField(max_length=255)

    def load_filter(self):
        filter_class = self.FILTER_TYPES[self.filter_class]
        kwargs = [arg.split('=') for arg in self.arguments.split('&')
                  if arg != '']
        filter = filter_class(type=self.type, source=self.source,
                              **dict(kwargs))
        return filter

    def __str__(self):
        return '%s %s %s' % (self.source, self.filter_class, self.arguments)


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
    allowed_sources = models.CharField(max_length=255, default=EarthImage.REDDIT, blank=True)
    history = models.CharField(max_length=255, default='', blank=True)
    contain_data_sources = models.CharField(max_length=255, default='', blank=True)
    relative_frequency = models.CharField(max_length=20, default='', blank=True)
    device_token = models.CharField(max_length=255, default='')
    is_administrator = models.BooleanField(default=False)
    align = models.IntegerField(default=0)

    def __str__(self):
        return self.url_identifier

    @classmethod
    def get_identifier(cls):
        """
        creates unique identifier to be used in URL
        """
        return str(sha1(urandom(6)).hexdigest())[:8]

    @property
    def frequencies(self):
        frequency = (1, 1, 1)
        try:
            frequency = tuple(
                int(f) for f in self.relative_frequency.split(',')
            )
        except (ValueError, TypeError):
            pass

        return frequency

    def update_history(self, image):
        HISTORY_LENGTH = 10
        ledger = self.history.split(',')
        ledger.insert(0, image.id)
        ledger = ledger[:HISTORY_LENGTH + 1]
        self.history = ','.join(map(str, ledger))
        self.save(update_fields=['history'])

    def filter_queryset(self, query_set):
        for source in EarthImage.SOURCES:
            if source not in self.allowed_sources:
                query_set = query_set.exclude(source=source)

        for filter_obj in self.filter_set.order_by('type'):
            filter_instance = filter_obj.load_filter()
            if filter_instance.source in self.allowed_sources:
                query_set = filter_instance(query_set)

        return query_set.values_list('id', flat=True)


class MarketingImage(models.Model):
    """
    EarthImage object that is especially well-suited to be displayed
    """
    image = models.ForeignKey(to=EarthImage)
    title = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class FavoriteImageItem(models.Model):
    """
    used for "favorite" functionality
    """
    image = models.ForeignKey(to=EarthImage)
    settings = models.ForeignKey(to=QuerySetting)
    create_date = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    lat = models.DecimalField(max_digits=16, decimal_places=12, null=True)
    long = models.DecimalField(max_digits=16, decimal_places=12, null=True)
    name = models.CharField(max_length=255)
    link = models.URLField(null=True)
    google_maps_url = models.URLField(null=True)

    def __str__(self):
        return self.name

    def get_maps_url(self):
        url = 'https://www.google.com/maps/?q={name}&t=k&zoom=20'.format(
            name='+'.join(self.name.split()),
        )
        return url