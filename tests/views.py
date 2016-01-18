import sys

from django import forms
from django.shortcuts import render

sys.path.insert(1, '../src')
print sys.path
from django_datatables import datatable



def main(request):

    return render(request, 'main.html', dict(
    ))
