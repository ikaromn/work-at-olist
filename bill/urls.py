from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from callcenter import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Billing API')

urlpatterns = [
    url(r'call-record/$', views.CallRecordCreate.as_view(),
        name='call_record_create'),
    url(r'bill/(?P<phone_number>[0-9]+)/$',
        views.BillByMonth.as_view(), name='bill_by_month'),
    url(r'price-rule/$', views.PriceRuleListCreate.as_view(),
        name='price_rule_list_create'),
    url(r'price-rule/(?P<pk>[0-9]+)/$', views.PriceRuleUpdate.as_view(),
        name='price_rule_update'),
    url(r'^docs/$', schema_view)
]
