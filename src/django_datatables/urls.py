try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import re_path

from .views import datatable_manager

app_name = 'django_datatables'

urlpatterns = [
    re_path(r'^data/$', datatable_manager, name="datatable_manager")
]
