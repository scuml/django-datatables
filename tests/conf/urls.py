"""datatbles URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import re_path

from django.conf.urls import include
from sample import views_sample

urlpatterns = [
    re_path(r'^$', views_sample.employee_list, name='employee_list'),
    re_path(r'^secure/$', views_sample.secure_employee_list, name='secure_employee_list'),
    re_path(r'^__django_datatables__/', include('django_datatables.urls')),
]
