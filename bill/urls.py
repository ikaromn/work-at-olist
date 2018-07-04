from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from callcenter import views
admin.autodiscover()


urlpatterns = [
    url(r'call-record/$', views.CallRecordCreate.as_view(),
        name='call-record-create'),
    url(r'bill/(?P<phone_number>[0-9]+)/$',
        views.BillByMonth.as_view(), name='bill-by-month'),
    url(r'^docs/$', views.schema_view, name="docs"),
    path('admin/', admin.site.urls),
]
