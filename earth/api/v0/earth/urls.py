from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^get/(?P<settings_uid>[a-zA-Z0-9]+)', views.EarthImageView.as_view(), name='settings-image'),
    url(r'^get/', views.EarthImageView.as_view(), name='random-image'),
    url(r'^settings/new/', views.QuerySettingCreate.as_view(), name='create-settings'),
    url(r'^settings/save/(?P<settings_uid>[a-zA-Z0-9]+)', views.QuerySettingSave.as_view(), name='put-settings'),
    url(r'^settings/(?P<settings_uid>[a-zA-Z0-9]+)', views.QuerySettingSave.as_view(), name='get-settings')
]
