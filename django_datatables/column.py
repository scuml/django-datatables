"""
Column classes
"""

from django.core.urlresolvers import reverse


class Column(object):

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, title=None, css_class=None, value=None, link=None, link_args=None):
        self.title = title
        self.value = value
        self.link = link
        self.css_class = css_class
        self.link_args = link_args or []

        # Increase the creation counter, and save our local copy.
        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    def render_column(self, value):
        """
        Returns a rendered value for the field.
        """
        return value

    def render_link(self, value, reverse_args):
        """
        Returns value wrapped in link tag as specified by link
        """
        link = reverse(self.link, args=reverse_args)
        return '<a href="{link}">{val}</a>'.format(link=link, val=value)

    def get_referenced_values(self):
        """ Returns a list of values that will need to be referenced """
        values = []
        if self.has_link():  # link will need link_args
            values.extend(self.link_args)
        return values

    def has_link(self):
        """ Returns True if column has link property set """
        return self.link is not None

    def get_reverse_args_from_values(self, values_dict):
        """
        Return a list of link args
        :param values_dict: one dict from Model.objects.values()
        :return: list corresponding to link_args and the input values_dict
        """
        return [values_dict[key] for key in self.link_args]


class TextColumn(Column):
    pass


class GlyphiconColumn(Column):

    def __init__(self, icon, *args, **kwargs):
        self.icon = icon

        self.constant = True
        return super(GlyphiconColumn, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return "<span class='glyphicon glyphicon-{}'></span>".format(self.icon)


class ConstantTextColumn(Column):

    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.constant = True
        return super(ConstantTextColumn, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return self.text


class DateColumn(Column):

    def render_column(self, value):
        return value.strftime("%Y-%b-%d").upper()
