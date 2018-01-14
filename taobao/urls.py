from django.conf.urls import url
from . import views
from django.urls import include, path

urlpatterns = [
    # 以index开头和结尾的url（也就是说就是index） django的url好像都要写成正则的形式

    url('^item/$', views.get_title_price, name='get_title_price'),
]
