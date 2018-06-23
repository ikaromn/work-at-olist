from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

from hello import views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'call-record/$', views.CallRecordCreate.as_view(), name='call-record-create'),
    path('admin/', admin.site.urls),
]
