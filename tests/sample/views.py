from django.shortcuts import render

from .models import Study
from django_datatables import datatable, column

class StudyListDatatable(datatable.Datatable):

    sponsor = column.TextColumn(value='sponsor__sponsor_name')
    protocol = column.TextColumn()
    study_name = column.TextColumn(link='edit_study', link_args=['slug'])
    activation_date = column.DateColumn()
    study_status = column.TextColumn(css_class='text-info')

    class Meta:
        model = Study
        order_columns = ('protocol', 'study_name')
        initial_order = ('study_name',)
        searching = True
        search_fields = ('protocol', 'study_name', 'sponsor__sponsor_name')

        export_to_excel = True

    def render_study_status(self, val):
        return val.title()

def study_list(request):
    datatable = StudyListDatatable()
    return render(request, 'main.html', {
        "datatable": datatable
    })


def edit_study(request, slug):
    return render(request, 'edit.html',
        {"slug": slug}
    )
