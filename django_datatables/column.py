
class Column(object):

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, label=None):
        self.label = label

        # Increase the creation counter, and save our local copy.
        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1


    def render_column(self, value):
        """
        Returns a rendered value for the field.
        """
        return value


class TextColumn(Column):
    pass


class DateColumn(Column):

    def render_column(self, value):
        return value.strftime("%Y-%b-%d").upper()
