from datetime import date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Wprowadź datę od teraz do 4 tygodni (domyślnie 3).')

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < date.today():
            raise ValidationError(_('Nieprawidłowa data - odnowienie w przeszłości'))

        if data > date.today() + timedelta(weeks=4):
            raise ValidationError(_('Nieprawidłowa data - odnowienie o ponad 4 tygodnie'))

        return data
