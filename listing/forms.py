from django.contrib.auth.models import User
from django import forms

from .models import Item


class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['item_name', 'description', 'city', 'contact_info', 'photo']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']