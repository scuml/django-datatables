"""
Datatable classes
"""

import logging
from json import dumps
import sys

from pyquerystring import parse

from django.conf import settings
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.views.debug import ExceptionReporter
from django.template.loader import select_template

from .column import *
from .mixins import DataResponse
from .datatable_meta import DeclarativeFieldsMetaclass

LOG = logging.getLogger(__name__)


class DatatableBase(metaclass=DeclarativeFieldsMetaclass):
    """ JSON data for datatables
    """
    class Meta:
        order_columns = []
        # max limit of records returned, do not allow to kill our server by huge sets of data
        max_display_length = 100
        extra_fields = []
        searching = False

    @property
    def _querydict(self):
        if self.request.method == 'POST':
            return self.request.POST

        return parse(self.request.GET)

    def get_column_titles(self):
        """ Return list of column titles for the template engine
        """
        titles = []
        for key, column in self.declared_fields.items():
            titles.append(column.title if column.title else key.replace("_", " ").title())
        return titles

    def get_values_list(self):
        """
        Returns a list of the values to retrieve from the ORM.
        Do not return columns marked as db_independant.
        """
        values = [
            c.value if c.value else k for k, c in self.declared_fields.items(
            ) if not getattr(c, 'db_independant', False)
        ]
        values.extend(self._meta.extra_fields)
        return values

    def get_referenced_values(self):
        """
        Returns a list of values to retrieve
        The values will need to be referenced but might not be displayed
        """
        referenced_values = []
        for column in self.declared_fields.values():
            referenced_values += column.get_referenced_values()
        return referenced_values

    def _render_column(self, field, column, ic):
        # Call the render_column method for each field
        for ir, row_dict in enumerate(self.values_dicts):
            self.rendered_columns[ir][ic] = column.render_column(row_dict.get(field))
            self.rendered_columns[ir][ic] = column.render_column_using_values(
                self.rendered_columns[ir][ic], row_dict)

    def execute_method(self, method, column, ic):
        for ir, row_dict in enumerate(self.values_dicts):
            if getattr(column, 'db_independant', False):
                # send row to db_indepenants
                self.rendered_columns[ir][ic] = method(row_dict)
            else:
                self.rendered_columns[ir][ic] = method(self.rendered_columns[ir][ic])

    def _render_field(self, field, column, ic):
        """ Call the render_{} method for each column in local class """
        method_name = "render_{}".format(field)
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                self.execute_method(method, column, ic)

    def _render_link(self, column, ic):
        """ Call the render_link to wrap column in link tag """
        for ir, row_dict in enumerate(self.values_dicts):
            self.rendered_columns[ir][ic] = column.render_link(
                self.rendered_columns[ir][ic], row_dict)

    def render_columns(self):
        """
        Renders a column on a row
        """
        fields = self.declared_fields.keys()
        self.rendered_columns = [[None] * len(fields) for i in range(len(self.values_dicts))]

        for ic, field in enumerate(fields):
            column = self.declared_fields[field]
            if column.value:
                field = column.value

            self._render_column(field, column, ic)
            self._render_field(field, column, ic)

            if column.has_link():
                self._render_link(column, ic)

        return self.rendered_columns

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order = []

        sorting_cols = self._querydict.get('order', {})
        for info in sorting_cols:
            column_index = int(info['column'])
            declared_fields_keys = list(self.declared_fields.keys())
            field = declared_fields_keys[column_index]
            column_key = self.declared_fields[field].value or field

            sort_dir = '-' if info['dir'] == 'desc' else ''
            order.append('{0}{1}'.format(sort_dir, column_key))

        if order:
            return qs.order_by(*order)
        return qs

    def paging(self, qs):
        """ Paging
        """
        limit = min(int(self._querydict.get('length', 25)), self._meta.max_display_length)
        start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        if limit == -1:
            return qs

        offset = start + limit

        return qs[start:offset]

    def get_initial_queryset(self, request):
        if not self._meta.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self._meta.model.objects.all()

    def filter_through_field_lookup(self, search):
        field_lookup_suffixes = ('exact', 'contains', 'startswith',
                                 'endswith', 'search', 'regex')

        for field_lookup in self._meta.search_fields:
            if not field_lookup.endswith(field_lookup_suffixes):
                    # if no suffix provided, append "__icontains"
                field_lookup += '__icontains'
            q |= Q(**{field_lookup: search})

        return q

    def filter_by_search(self, qs):
        """
        Filter queryset as specified by search_fields
        Searches on icontains unless otherwise specified
        """
        search = self.request.GET.get('search[value]', None)
        if not search:
            return qs

        if getattr(self._meta, 'search_min_length', 0) <= len(search) and hasattr(
                self._meta, "search_fields"):
            q = Q()
            q = self.filter_through_field_lookup(search)
            qs = qs.filter(q)

        return qs

    def prepare_results(self, qs):
        values_to_get = set(self.get_values_list())
        values_to_get = values_to_get.union(set(self.get_referenced_values()))
        self.values_dicts = qs.values(*values_to_get)

        rendered_values = self.render_columns()
        data = [row for row in rendered_values]
        return data

    def get_data(self, request):
        """
        Gets all data, unpaged, as a list of dicts.
        """
        try:
            qs = self.get_initial_queryset(request)
            qs = self.filter_by_search(qs)
            qs = self.ordering(qs)
            data = self.prepare_results(qs)
        except Exception as e:
            LOG.exception(str(e))
            data = {'error': self.report_traceback()}
        return data

    def get_context_data(self, request):
        """
        Gets paginated data.
        Returned as json dict.
        """

        json_response = dict(draw=0, recordsTotal=0, recordsFiltered=0, data=[])

        additional_data = request.GET.get("additional_data")
        filter_params = parse(additional_data) if additional_data else {}
        try:
            qs = self.get_initial_queryset(request)
            total_records = qs.count()
            qs = self.filter_by_search(qs)
            if filter_params:
                qs = qs.filter(**filter_params)

            # number of records after filtering
            total_display_records = qs.count()

            qs = self.ordering(qs)
            qs = self.paging(qs)
            data = self.prepare_results(qs)
            json_response.update({"draw": int(self._querydict.get('draw', 0)),
                                  "recordsTotal": total_records,
                                  "recordsFiltered": total_display_records,
                                  "data": data})

        except Exception as e:
            LOG.exception(str(e))
            json_response['error'] = self.report_traceback()

        return json_response

    def report_traceback(self):
        if settings.DEBUG:
            reporter = ExceptionReporter(None, *sys.exc_info())
            return "\n" + reporter.get_traceback_text()
        return "\nAn error occured while processing an AJAX request."


class Datatable(DatatableBase, DataResponse):

    def _config_columns(self):
        columns = []
        for key, column in self.declared_fields.items():
            column_config = {}
            if column.css_class:
                column_config['className'] = column.css_class
            if key not in self._meta.order_columns:
                column_config['orderable'] = False
            columns.append(column_config)

        return columns

    def _config_order(self):
        order = []
        for order_col in self._meta.initial_order:
            order_dir = 'asc'
            if order_col.startswith('-'):
                order_col = order_col[1:]
                order_dir = 'desc'
            declared_fields_keys = list(self.declared_fields.keys())
            order_index = declared_fields_keys.index(order_col)
            order.append([order_index, order_dir])

        return order

    def datatable_config(self):
        """
        Returns the json config for the datatables init method in javascript
        """
        config = {}

        config['columns'] = self._config_columns()
        config['searching'] = self._meta.searching
        config['order'] = self._config_order() if "initial_order" in self._meta else []

        # Initial Display Length
        config['iDisplayLength'] = self._meta.get('initial_rows_displayed', 25)
        config['serverSide'] = self._meta.get('server_side', True)

        return mark_safe(dumps(config))

    @property
    def filter_form(self):
        return self._meta.get('filter_form', None)

    def render(self):
        """
        Render the javascript and html to create the datatable
        """
        template = select_template(['django_datatables/table.html'])
        context = {
            "can_export_to_excel": self._meta.get('export_to_excel', False),
            "module": self.__module__,
            "name": self.__class__.__name__,
            "datatable": self,
        }
        template_content = template.render(context)
        return mark_safe(template_content)
