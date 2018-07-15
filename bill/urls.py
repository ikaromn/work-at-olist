from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from callcenter import views
from callcenter import schemas
admin.autodiscover()


urlpatterns = [
    url(r'call-record/$', views.CallRecordCreate.as_view(),
        name='call_record_create'),
    url(r'bill/(?P<phone_number>[0-9]+)/$',
        views.BillByMonth.as_view(), name='bill_by_month'),
    url(r'price-rule/$', views.PriceRuleListCreate.as_view(),
        name='price_rule_list_create'),
    url(r'price-rule/(?P<pk>[0-9]+)/$', views.PriceRuleUpdate.as_view(),
        name='price_rule_update'),
    url(r'^docs/$', schemas.SwaggerSchemaView.as_view(),
        name="docs"),
    path('admin/', admin.site.urls),
]
