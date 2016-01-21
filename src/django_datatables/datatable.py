"""
Datatable classes
"""

from collections import OrderedDict
import logging
from json import dumps

from pyquerystring import parse

from django.conf import settings
from django.db.models import Q
from django.utils import six
from django.utils.safestring import mark_safe

from .column import *
from .mixins import JSONResponseView

logger = logging.getLogger(__name__)


class AttrDict(dict):
    marker = object()

    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, AttrDict):
            value = AttrDict(value)
        super(AttrDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        found = self.get(key, AttrDict.marker)
        if found is AttrDict.marker:
            found = AttrDict()
            super(AttrDict, self).__setitem__(key, found)
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    _meta = AttrDict()

    def __new__(mcs, name, bases, attrs):

        attr_meta = attrs.pop('Meta', None)

        # Collect fields from current class.
        current_columns = []
        for key, value in list(attrs.items()):
            if isinstance(value, Column):
                current_columns.append((key, value))
                attrs.pop(key)
        current_columns.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_columns)

        new_class = (super(DeclarativeFieldsMetaclass, mcs)
            .__new__(mcs, name, bases, attrs))

        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        base_meta = getattr(new_class, '_meta', None)

        if meta:
            for key, value in meta.__dict__.items():
                setattr(base_meta, key, value)

            setattr(new_class, '_meta', base_meta)


        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class DatatableBase(six.with_metaclass(DeclarativeFieldsMetaclass)):
    """ JSON data for datatables
    """

    class Meta:
        order_columns = []
        max_display_length = 100  # max limit of records returned, do not allow to kill our server by huge sets of data
        extra_fields = []

    @property
    def _querydict(self):
        if self.request.method == 'POST':
            return self.request.POST
        else:
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
        values = []
        for key, column in self.declared_fields.items():
            if getattr(column, 'db_independant', False):
                continue
            values.append(column.value if column.value else key)
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

    def get_field_by_index(self, index):
        """
        Returns the column key at a specified index
        """
        keys = self.declared_fields.keys()
        return keys[index]

    def get_index_by_key(self, key):
        """
        Returns the column index for a provided key
        """
        keys = self.declared_fields.keys()
        return keys.index(key)

    def render_columns(self, row_dicts):
        """ Renders a column on a row
        """
        fields = self.declared_fields.keys()
        rendered_columns = []  # initialize return array
        for i in range(len(row_dicts)):
            rendered_columns.append([None] * len(fields))

        for ic, field in enumerate(fields):
            column = self.declared_fields[field]
            if column.value:
                field = column.value

            # Call the render_column method for each field
            for ir, row_dict in enumerate(row_dicts):
                rendered_columns[ir][ic] = column.render_column(row_dict.get(field))
                rendered_columns[ir][ic] = column.render_column_using_values(
                    rendered_columns[ir][ic], row_dict
                )

            # Call the render_{} method for each column in local class
            method_name = "render_{}".format(field)
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    for ir, row_dict in enumerate(row_dicts):
                        if getattr(column, 'db_independant', False):
                            # send row to db_indepenants
                            rendered_columns[ir][ic] = method(row_dict)
                        else:
                            rendered_columns[ir][ic] = method(rendered_columns[ir][ic])

            if column.has_link():
                # Call the render_link to wrap column in link tag
                for ir, row_dict in enumerate(row_dicts):
                    rendered_columns[ir][ic] = column.render_link(
                        rendered_columns[ir][ic], row_dict
                    )

        return rendered_columns

    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order = list()

        sorting_cols = self._querydict.get('order', {})
        for info in sorting_cols:
            column_index = int(info['column'])
            sort_dir = '-' if info['dir'] == 'desc' else ''
            field = self.get_field_by_index(column_index)
            column_key = self.declared_fields[field].value
            if not column_key:
                column_key = field
            order.append('{0}{1}'.format(sort_dir, column_key))

        if order:
            return qs.order_by(*order)
        return qs

    def paging(self, qs):
        """ Paging
        """
        limit = min(int(self._querydict.get('length', 10)), self._meta.max_display_length)
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

    def extract_datatables_column_data(self):
        """ Helper method to extract columns data from request as passed by Datatables 1.10+
        """
        request_dict = self._querydict
        col_data = []
        counter = 0
        data_name_key = 'columns[{0}][name]'.format(counter)
        while data_name_key in request_dict:
            searchable = True if request_dict.get('columns[{0}][searchable]'.format(counter)) == 'true' else False
            orderable = True if request_dict.get('columns[{0}][orderable]'.format(counter)) == 'true' else False

            col_data.append({'name': request_dict.get(data_name_key),
                             'data': request_dict.get('columns[{0}][data]'.format(counter)),
                             'searchable': searchable,
                             'orderable': orderable,
                             'search.value': request_dict.get('columns[{0}][search][value]'.format(counter)),
                             'search.regex': request_dict.get('columns[{0}][search][regex]'.format(counter)),
                             })
            counter += 1
            data_name_key = 'columns[{0}][name]'.format(counter)
        return col_data

    def filter_by_search(self, qs):
        """
        Filter queryset as specified by search_fields
        Searches on icontains unless otherwise specified
        """
        search = self.request.GET.get('search[value]', None)
        if search:
            if getattr(self._meta, 'search_min_length', 0) <= len(search):
                if hasattr(self._meta, "search_fields"):
                    field_lookup_suffixes = (
                        'exact', 'contains', 'startswith',
                        'endswith', 'search', 'regex'
                    )
                    q = Q()
                    for field_lookup in self._meta.search_fields:
                        if not field_lookup.endswith(field_lookup_suffixes):
                            # if no suffix provided, append "__icontains"
                            field_lookup += '__icontains'
                        q |= Q(**{field_lookup: search})
                    qs = qs.filter(q)

        return qs

    def filter_by_filters(self, qs):
        return qs

    def filter_queryset(self, qs):
        qs = self.filter_by_search(qs)
        qs = self.filter_by_filters(qs)
        return qs

    def prepare_results(self, qs):
        values_to_get = set(self.get_values_list())
        values_to_get = values_to_get.union(set(self.get_referenced_values()))
        values_dicts = qs.values(*values_to_get)

        rendered_values = self.render_columns(values_dicts)
        data = []
        for row in rendered_values:
            data.append(row)
        return data

    def get_data(self):
        """
        Gets all data, unpaged, as a list of dicts.
        """
        try:
            qs = self.get_initial_queryset()
            qs = self.filter_queryset(qs)
            qs = self.ordering(qs)
            data = self.prepare_results(qs)
        except Exception as e:
            logger.exception(str(e))

            if settings.DEBUG:
                import sys
                from django.views.debug import ExceptionReporter
                reporter = ExceptionReporter(None, *sys.exc_info())
                text = "\n" + reporter.get_traceback_text()
            else:
                text = "\nAn error occured while processing an AJAX request."

            data = {'error': text}
        return data


    def get_context_data(self, request):

        try:
            qs = self.get_initial_queryset(request)

            # number of records before filtering
            total_records = qs.count()

            qs = self.filter_queryset(qs)

            # number of records after filtering
            total_display_records = qs.count()

            qs = self.ordering(qs)
            qs = self.paging(qs)
            # prepare output data
            data = self.prepare_results(qs)

            ret = {'draw': int(self._querydict.get('draw', 0)),
                   'recordsTotal': total_records,
                   'recordsFiltered': total_display_records,
                   'data': data
            }
        except Exception as e:
            logger.exception(str(e))

            if settings.DEBUG:
                import sys
                from django.views.debug import ExceptionReporter
                reporter = ExceptionReporter(None, *sys.exc_info())
                text = "\n" + reporter.get_traceback_text()
            else:
                text = "\nAn error occured while processing an AJAX request."

            ret = {'error': text,
                   'data': [],
                   'recordsTotal': 0,
                   'recordsFiltered': 0,
                   'draw': int(self._querydict.get('draw', 0))}
        return ret


from django.template.loader import select_template


class Datatable(DatatableBase, JSONResponseView):

    def datatable_config(self):
        """
        Returns the json config for the datatables init method in javascript
        """
        config = dict(
            columns=list()
        )

        # Column config
        for key, column in self.declared_fields.items():
            column_config = dict()
            if column.css_class:
                column_config['className'] = column.css_class
            if key not in self._meta.order_columns:
                column_config['orderable'] = False
            config['columns'].append(column_config)

        # Ordering
        config['order'] = []
        if hasattr(self._meta, "initial_order"):
            for order_col in self._meta.initial_order:
                order_dir = 'asc'
                if order_col.startswith('-'):
                    order_col = order_col[1:]
                    order_dir = 'desc'
                order_index = self.get_index_by_key(order_col)
                config['order'].append([order_index, order_dir])

        # Initial Display Length
        config['iDisplayLength'] = getattr(self._meta, 'initial_rows_displayed', 10)

        return mark_safe(dumps(config))

    def render(self):
        """
        Render the javascript and html to create the datatable
        """
        template = select_template(['django_datatables/table.html'])
        context = dict(
            can_export_to_excel=getattr(self._meta, 'export_to_excel', False),
            module=self.__module__,
            name=self.__class__.__name__,
            datatable=self,
        )
        template_content = template.render(context)
        return mark_safe(template_content)
