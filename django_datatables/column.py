"""
Column classes
"""

from django.core.urlresolvers import reverse


class Column(object):

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, label=None, link=None, link_args=None):
        self.label = label
        self.link = link
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


class DateColumn(Column):

    def render_column(self, value):
        return value.strftime("%Y-%b-%d").upper()
