from django.shortcuts import render

from .models import Employee
from django_datatables import datatable, column

from django.contrib.auth.mixins import LoginRequiredMixin

class EmployeeListDatatable(datatable.Datatable):
    name = column.StringColumn()
    birthday = column.DateColumn()
    start_date = column.DateColumn()
    manager = column.TextColumn(value='manager__last_name')

    def render_name(self, row):
        return "{} {}".format(row['first_name'], row['last_name']).strip()

    class Meta:
        model = Employee
        extra_fields = ('first_name', 'last_name')


class SecureEmployeeListDatatable(LoginRequiredMixin, EmployeeListDatatable):

    def get_initial_queryset(self, request):
        return Employee.objects.filter(first_name="Fred")

def employee_list(request):
    datatable = EmployeeListDatatable()
    return render(request, 'main.html',
        {"datatable": datatable}
    )

def secure_employee_list(request):
    datatable = SecureEmployeeListDatatable()
    return render(request, 'main.html',
        {"datatable": datatable}
    )