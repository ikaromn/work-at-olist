from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from hello import views
admin.autodiscover()


urlpatterns = [
    url(r'call-record/$', views.CallRecordCreate.as_view(),
        name='call-record-create'),
    url(r'bill/(?P<phone_number>[0-9]+)/(?:(?P<month>[0-9]+)/\
        (?:(?P<year>[0-9]+))/)?$',
        views.BillByMonth.as_view(), name='bill-by-month'),
    path('admin/', admin.site.urls),
]
