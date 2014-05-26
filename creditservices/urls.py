
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^info/(?P<uid>\d+)/$', views.InfoView.as_view(),
        name='creditinfo'),
    url(r'^creditlist/$', views.CreditLIstView.as_view(),
        name='creditlist'),
)
