from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Profile


class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['item_name', 'description', 'city', 'contact_info', 'photo', 'another_photo', 'and_another_photo']


# form for add item page
class ItemFormForAdd(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['photo', 'another_photo', 'and_another_photo', 'item_name', 'description']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['city', 'contact_info']


# not used
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
