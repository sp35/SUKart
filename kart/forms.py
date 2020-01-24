from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm

from .models import User, DeliveryAgent, ShoppingUser


class DeliveryAgentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'name', 'email', 'dob', 'state', 'city', 'password1', 'password2']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_delivery_agent = True
        user.save()
        delivery_agent = DeliveryAgent.objects.create(user=user)
        return user


class ShoppingUserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'name', 'email', 'dob', 'state', 'city', 'password1', 'password2']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_shopping_user = True
        user.save()
        shopping_user = ShoppingUser.objects.create(user=user)
        return user


class SearchForm(forms.Form):
    query = forms.CharField(max_length=20, required=False, label="", widget=forms.TextInput(attrs={'placeholder': 'Search by name'}))