from functools import partial

from django import forms

LogMessageField = partial(forms.CharField, max_length=400, required=False)
