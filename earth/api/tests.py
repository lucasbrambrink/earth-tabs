from django.shortcuts import reverse
from django.test.client import RequestFactory
from django.test import TestCase
from .models import EarthImage, QuerySetting, Filter
from .v0.earth.views import EarthImageView
from . import filters


class ApiTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ApiTests, cls).setUpClass()
        cls.test_setting = QuerySetting.objects.create(
            url_identifier='test',
        )
        cls.api = EarthImageView()

    @classmethod
    def request(cls, url, request_type='get', data=None, **kwargs):
        factory = RequestFactory()
        if request_type == 'post':
            data = data or {}
            request = factory.post(url, data)
        else:
            request = factory.get(url)

        return request

    def get_api_response(self, url_name, url_kwargs, **kwargs):
        url = reverse(url_name, kwargs=url_kwargs)
        request = self.request(url, 'get', **kwargs)
        response = self.api.get(request, **url_kwargs)
        return response.data

    @classmethod
    def create_image(cls, **kwargs):
        kwargs['is_public'] = kwargs.get('is_public', True)
        kwargs['score'] = kwargs.get('score', 100)
        earth_image = EarthImage.objects.create(**kwargs)
        return earth_image

    def test_api_get_no_settings(self):
        permalink_test_name = 'test'
        self.create_image(**{'permalink': permalink_test_name})
        image_data = self.get_api_response('random-image', {})
        self.assertEqual(image_data.get('permalink'), permalink_test_name)

    def test_api_get_with_settings(self):
        permalink_test_name = 'reddit'
        self.create_image(**{'permalink': permalink_test_name, 'source': EarthImage.REDDIT})
        self.create_image(**{'permalink': 'apod', 'source': EarthImage.APOD})

        test_setting = QuerySetting.objects.create(
            url_identifier='only-reddit',
            allowed_sources=','.join(EarthImage.APOD)
        )

        url_kwargs = {'settings_uid': test_setting.url_identifier}
        image_data = self.get_api_response('settings-image', url_kwargs)
        self.assertEqual(image_data.get('permalink'), permalink_test_name)

    def test_api_get_with_filters(self):
        self.create_image(**{'title': 'test', 'source': EarthImage.REDDIT})

        TARGET_VALUE = 'foo'
        self.create_image(**{'title': TARGET_VALUE, 'source': EarthImage.REDDIT})

        Filter.objects.create(
            setting=self.test_setting,
            source=EarthImage.REDDIT,
            filter_class=Filter.QUERY,
            type=filters.Filter.SOURCE_SPECIFIC,
            arguments='key_words={}'.format(TARGET_VALUE)
        )

        url_kwargs = {'settings_uid': self.test_setting.url_identifier}
        image_data = self.get_api_response('settings-image', url_kwargs)
        self.assertEqual(image_data.get('title'), TARGET_VALUE)

