from django import forms


class EmployeeFilterForm(forms.Form):
    last_name__icontains = forms.CharField(label="Last Name", required=False)
