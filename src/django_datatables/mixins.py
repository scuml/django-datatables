from datetime import datetime
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
try:
    from django.utils.encoding import force_str
except ImportError:
    from django.utils.encoding import force_text as force_str
from django.utils.functional import Promise
try:
    from django.utils.translation import gettext as _
except ImportError:
    from django.utils.translation import ugettext as _
from django.utils.cache import add_never_cache_headers

try:
    from .excel import ExcelWriter
except ImportError:
    ExcelWriter = None

LOG = logging.getLogger(__name__)


class LazyEncoder(DjangoJSONEncoder):
    """Encodes django's lazy i18n strings
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super(LazyEncoder, self).default(obj)


class DataResponse(object):

    def create_excel_response(self, request):
        """
        Return an excel writer as a response.
        """
        headers = self.get_column_titles()
        rows = self.get_data(request)
        title = getattr(self._meta, "title", "Sheet")

        xlwriter = ExcelWriter()
        xlwriter.add_headers(title, headers)
        for row in rows:
            xlwriter.add_row(title, dict(zip(headers, row)))

        return xlwriter.download(f'{title}-{datetime.now().strftime("%Y-%m-%d %H%m")}.xlsx')

    def create_data_response(self, func_val, request):
        try:
            assert isinstance(func_val, dict)
            response = dict(func_val)
            if 'result' not in response:
                response['result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception as e:
            LOG.exception('JSON view error: %s', request.path)
            msg = getattr(e, 'message', _('Internal error') + ': ') + str(e)
            response = {'result': 'error', 'sError': msg, 'text': msg}

        return JsonResponse(response)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = None

        if request.GET.get("export") == "excel":
            return self.create_excel_response(request)

        func_val = self.get_context_data(request)
        response = self.create_data_response(func_val, request)

        add_never_cache_headers(response)
        return response
