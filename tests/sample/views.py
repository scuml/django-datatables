from django.shortcuts import render

from .models import Employee
from django_datatables import datatable, column

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

def employee_list(request):
    datatable = EmployeeListDatatable()
    return render(request, 'main.html',
        {"datatable": datatable}
    )
