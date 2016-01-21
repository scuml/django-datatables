Django Datatables
======

The django datatables library makes creating tables that make use of the datatables library simple, reusable, pythonic, djangoesque, and quite a bit fun.

**Project Goals**

* Allow creation of tables in a style similar to django forms.
* Remove tedious editing of datatables javascript config to match columns.
* Configure ajax URLs automagically.
* Simplify use of Django style URLs within the datatable


Quick Setup
-----
Download the library and place it somewhere accessable in your PYTHONPATH.  The following is a basic example to demonstrate the ease to get up and running.

**settings.py**

Add `django_datables` to the `INSTALLED_APPS` setting.

```python
INSTALLED_APPS = [
    ...
    'django_datatables',
    ...
]
```

**urls.py**

Add the following line to urls.py.

```python
    url(r'^__django_datatables__/', include('django_datatables.urls')),
```

**views.py**

```python
    from django_datatables.datatable import *
    from django_datatables import column

    class StudyListDatatable(Datatable):
        code_name = column.TextColumn()

        class Meta:
            model = Study

    def study_list(request)
        datatable = StudyListDatatable()
        return render(request, 'datatables_demo.html',
            {"datatable": datatable}
        )
```


**Template**

```python
    {{datatable.render}}
```

Building Up
-----------

**Custom Title/Value**

In the example shown, the code_name, as the variable name is automatically used to fetch the field and then used as the header for the column.  There will often be cases where the variable name will not coincide to either of these and can be overritten with the following:

```python
    created_date = column.TextColumn(title='Made on')
    scientist = column.TextColumn(value='scientist__scientist_name')
```

**CSS Class**

A css class to apply to each cell in the column.

```python
    scientist = column.TextColumn(css_class='text-danger')
```

**Joined tables**

Fields in joined tables are accessed using the same syntax used in django.

```python
    scientist = column.TextColumn(value='scientist__scientist_name')
```

**Adding links**

Links support django's URL dispatcher.  Just add the URL name to the link attribute and the arguments that get passed to the link.  You don't even need the column listed -- Django Datables will integentally fetch the needed field and populate the links accordingly.

```python
    code_name = column.TextColumn(link='edit_study', link_args=['slug'])
```

**Data from multiple fields**

To pull data from multiple fields into one column, declare the column as a `StringColumn`.  If needed, add the fields to be requested from the database in the `Meta.extra_fields` attribute.  Finally, render the desired with the render_* method.

```python
    name = column.StringColumn()
    class Meta:
        model = Employee
        extra_fields = ('first_name', 'last_name')
    def render_name(self, row):
        return "{} {}".format(row['first_name'], row['last_name']).strip()


```

Meta
----

**model**: the primary model to be displayed in the table

```python
    model = Study
```

**order_columns**: a list of the columns that can be sorted

```python
    order_columns = ['study_name', 'created_date', 'modified_date', 'scientist']
```

**initial_order**: the inital sort of the table

```python
    initial_order = ['created_date', 'scientist']
```

**search_fields**the fields that the search box will search for content.  This can be more finely controlled in the filter_by_search() method.

```python
    search_fields = ['study_name', 'code_name', 'scientist__scientist_name']
```

**title**: The title of the report.  Only used for the filename and sheet name of the excel export.

```python
    title = "Study List"
```

**export_to_excel**: If openpyxl is installed and set to true, will display a link to download an excel file containing all rows in the table.

```python
    export_to_excel = True
```

Custom rendering
-------

Any field can have it's render method extended using render_*

```python
    def render_code_name(self, value):
        return value.lower()

    def render_created_date(self, value):
        return value.strftime("%m/%d/%Y")
```


Columns
-------

**Attributes**

* title - Displayed in the header
* css_class - A CSS class to apply to the column
* value - The value in the database to use
* link - The django url name this column will link to
* link_args - the link arguments

The following column types are available in the django_datatables.column module.

**TextColumn**: A standard column that will display the contents of a single field.

**ConstantTextColumn(text)**: Will display text independant of the database.  Ex: Edit, or Delete

**StringColumn**: A column that will render text using multiple fields.  Request the data with `Meta.extra_fields` and format the text with the render_* method.

**CheckBoxColumn**: Renders a checkbox.

**GlyphiconColumn(icon)**: Displays an icon from bootstrap's v3 glyphicon set.

**DateColumn**: Renders a date in Y-m-d format.


*To Do*
-------

* Attach a django form to filter the table.
* Simple way to enforce security (e.g. login_required)