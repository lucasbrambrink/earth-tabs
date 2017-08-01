from django.conf.urls import url, include

from .views import EarthImageView

urlpatterns = [
    url(r'^get/(?<settings_uid>[a-zA-Z0-9]+)', EarthImageView.as_view(), name='random-image'),
    url(r'^get/', EarthImageView.as_view(), name='random-image')
]
