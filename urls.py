from django.conf.urls import url, include
from django.contrib import admin
from website import urls as website_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(website_urls)),
]
