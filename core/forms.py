from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from core.models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'privacy_mode', 'lunches_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


# class LunchScheduleForm(forms.ModelForm):
#     class Meta:
#         model = LunchSchedule
#         fields = ['weekday', 'confirm_delta', 'confirm_timeout']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.add_input(Submit('submit', 'Submit'))
