# forms.py

from django import forms
from .models import Subject


class CustomQuizForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    number_of_questions = forms.IntegerField(
        min_value=1, max_value=100)  # Adjust max_value as needed
