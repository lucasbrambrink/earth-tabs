from django.conf.urls import url, include

urlpatterns = [
    url(r'^v0/earth/', include('api.v0.earth.urls'))
]
