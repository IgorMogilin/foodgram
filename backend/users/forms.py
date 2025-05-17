from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RequiredFieldsUserCreationForm(UserCreationForm):
    """Форма создания пользователя с обязательными полями."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="Имя")
    last_name = forms.CharField(required=True, label="Фамилия")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
