from __future__ import unicode_literals

from django.db import models

class Employee(models.Model):

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField()
    start_date = models.DateField()
    manager = models.ForeignKey('self', null=True)
