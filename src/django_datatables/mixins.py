from datetime import datetime
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.translation import ugettext as _
from django.utils.cache import add_never_cache_headers

try:
    from .excel import ExcelWriter
except ImportError:
    ExcelWriter = None

import logging
logger = logging.getLogger(__name__)


class LazyEncoder(DjangoJSONEncoder):
    """Encodes django's lazy i18n strings
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class DataResponse(object):

    def render_to_json_response(self, context):
        """ Returns a JSON response containing 'context' as payload
        """
        response = HttpResponse(
            context,
            content_type='application/json',
        )
        add_never_cache_headers(response)
        return response

    def create_excel_response(self, request):
        """

        """
        headers = self.get_column_titles()
        rows = self.get_data(request)
        title = getattr(self._meta, "title", "Sheet")

        xlwriter = ExcelWriter()
        xlwriter.add_headers(title, headers)
        for row in rows:
            xlwriter.add_row(title, dict(zip(headers, row)))

        return xlwriter.download(
            '{}-{}.xlsx'.format(
                title, datetime.now().strftime("%Y-%m-%d %H%m")
            )
        )

    def as_json(self, request, *args, **kwargs):
        self.request = request
        response = None

        if request.GET.get("export") == "excel":
            return self.create_excel_response(request)

        func_val = self.get_context_data(request)
        try:
            assert isinstance(func_val, dict)
            response = dict(func_val)
            if 'result' not in response:
                response['result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception as e:
            logger.error('JSON view error: %s' % request.path, exc_info=True)

            # Come what may, we're returning JSON.
            if hasattr(e, 'message'):
                msg = e.message
                msg += str(e)
            else:
                msg = _('Internal error') + ': ' + str(e)
            response = {'result': 'error',
                        'sError': msg,
                        'text': msg}

        dump = json.dumps(response, cls=LazyEncoder)
        return self.render_to_json_response(dump)
