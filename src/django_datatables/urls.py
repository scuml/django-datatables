from __future__ import unicode_literals
from django.conf.urls import *

from .views import datatable_manager

app_name = 'django_datatables'

urlpatterns = [
    url(r'^data/$', datatable_manager, name="datatable_manager")
]
