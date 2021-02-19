from django import forms
from pkg_resources import require
from .models import Document, Patient , TestResult , Comparison

# thirdparty import
from bootstrap_datepicker_plus import DatePickerInput

class ComparisonForm(forms.Form):
    from_unit = forms.CharField(label='from_unit', max_length=55, required=True)
    to_unit = forms.CharField(label='to_unit', max_length=55, required=True)
    multiplier = forms.FloatField(label='multiplier',required=True)
    adder = forms.FloatField(label='adder',required=True)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('name', 'document', 'report')

class LabelForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ('label', 'value','unit')

class GeneratedReportForm(forms.Form):
    document1 = forms.ModelChoiceField(queryset=Document.objects.all())
    document2 = forms.ModelChoiceField(queryset=Document.objects.all())

    def __init__(self, *args, **kwargs):
        """
        to filter queryset based on patient pk, must pass pk in kwargs
        """
        pk = kwargs.pop('pk', None)
        super(GeneratedReportForm, self).__init__(*args, **kwargs)

        if pk is not None:
            self.fields['document1'].queryset = Document.objects.filter(patient_id=pk)
            self.fields['document2'].queryset = Document.objects.filter(patient_id=pk)

class PatientSearchForm(forms.Form):
    name = forms.CharField(label='Patient name', max_length=255, required=False)
    start_date = forms.DateField(
        required=False,
        widget=DatePickerInput()
    )
    end_date = forms.DateField(
        required=False,
        widget=DatePickerInput()
    )
