from django.conf.urls import url, include

from .views import EarthImageView

urlpatterns = [
    url(r'^get/', EarthImageView.as_view(), name='random-image')
]
