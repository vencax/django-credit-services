
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^info/(?P<company_id>\d+)/$', views.InfoView.as_view(),
        name='creditinfo'),
)
