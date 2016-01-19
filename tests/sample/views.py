from django.shortcuts import render

from .models import Employee
from django_datatables import datatable, column

class EmployeeListDatatable(datatable.Datatable):
    first_name = column.TextColumn()
    last_name = column.TextColumn()
    birthday = column.DateColumn()
    start_date = column.DateColumn()
    manager = column.TextColumn(value='manager__last_name')

    class Meta:
        model = Employee

def employee_list(request):
    datatable = EmployeeListDatatable()
    return render(request, 'main.html',
        {"datatable": datatable}
    )
