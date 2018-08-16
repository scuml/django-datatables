"""
Column classes
"""

from django.urls import reverse


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

    def render_column_using_values(self, value, values_dict):
        """
        Return a rendered value which need to reference the Model's values dict
        """
        return value

    def get_referenced_values(self):
        """ Returns a list of values that will need to be referenced """
        values = []
        if self.has_link():  # link will need link_args
            for link_arg in self.link_args:
                if link_arg[0] not in (".", "#"):
                    values.append(link_arg)

        if type(self) == CheckBoxColumn:  # CheckBoxColumn's "value" is a field
            values.append(self.value)
        return values

    def render_link(self, value, values_dict):
        """
        Returns value wrapped in link tag as specified by link
        """
        def get_link_val(key):
            """ Gets a link by column, fixed string (#), or class attribute (.)"""
            if key.startswith("#"):
                return key[1:]
            elif key.startswith("."):
                return getattr(self, key[1:])
            return values_dict[key]

        reverse_args = [get_link_val(key) for key in self.link_args]
        link = reverse(self.link, args=reverse_args)
        return '<a href="{link}">{val}</a>'.format(link=link, val=value)

    def has_link(self):
        """ Returns True if column has link property set """
        return self.link is not None


class TextColumn(Column):
    pass


class CheckBoxColumn(Column):

    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        self.db_independant = True
        super(CheckBoxColumn, self).__init__(*args, **kwargs)

    def render_column_using_values(self, value, values_dict):
        return '<input id="{id}" type="checkbox" name="{name}" value="{value}"></>'.format(
            id='???',
            name=self.name if self.name else '',
            value=values_dict[self.value],
        )


class GlyphiconColumn(Column):

    def __init__(self, icon, *args, **kwargs):
        self.icon = icon
        self.db_independant = True
        super(GlyphiconColumn, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return "<span class='glyphicon glyphicon-{}'></span>".format(self.icon)


class FontAwesome4Column(Column):

    def __init__(self, icon, *args, **kwargs):
        if icon.startswith('fa-'):
            icon = icon[3:]
        self.icon = icon
        self.db_independant = True
        super(FontAwesome4Column, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return """<i class="fa fa-{}" aria-hidden="true"></i>""".format(self.icon)


class FontAwesome5Column(Column):

    def __init__(self, icon, *args, **kwargs):
        self.icon = icon
        self.db_independant = True
        super(FontAwesome5Column, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return """<i class="{}"></i>""".format(self.icon)


class BulletedListColumn(Column):

    def render_column(self, value):
        items = '\n'.join(map(lambda v: f'<li>{v}</li>', value))

        return f"""
            <ul style="margin: 0; padding-left: 1.5em;">
                {items}
            </ul>
        """


class ConstantTextColumn(Column):

    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.db_independant = True
        super(ConstantTextColumn, self).__init__(*args, **kwargs)

    def render_column(self, value):
        return self.text


class DateColumn(Column):
    """
    Renders a date in Y-m-d format
    """
    def render_column(self, value):
        if value:
            return value.strftime("%Y-%m-%d").upper()
        return ''


class StringColumn(Column):
    """
    Does not ask the database for a column.  Used to custom render
    values from other columns.
    """
    def __init__(self, *args, **kwargs):
        self.db_independant = True
        super(StringColumn, self).__init__(*args, **kwargs)
