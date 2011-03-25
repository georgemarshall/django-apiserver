# encoding: utf-8

from django import forms

METHODS = (
    ('get', 'GET'),
    ('post', 'POST'),
    ('put', 'PUT'),
    ('delete', 'DELETE'),
    )

class RequestForm(forms.Form):
    method = forms.ChoiceField(choices=METHODS, initial='GET', required=False)
    endpoint = forms.CharField(max_length=200, initial='/v1', required=False)
    user = forms.ChoiceField(choices=(('', '',)), required=False) # initial=default_user[0]
    data = forms.CharField(widget=forms.widgets.Textarea, initial='', required=False)