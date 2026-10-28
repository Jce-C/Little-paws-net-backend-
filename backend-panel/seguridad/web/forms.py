from django.utils.translation import gettext_lazy as _t
from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'username', 'placeholder': 'tu@organizacion.org'}))
    password = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'placeholder': _t('Ingresa tu contraseña')}))
    captcha_token = forms.UUIDField(widget=forms.HiddenInput())
    captcha = forms.IntegerField(min_value=0, max_value=30, widget=forms.NumberInput(attrs={'inputmode': 'numeric', 'autocomplete': 'off', 'placeholder': _t('Tu respuesta')}))

    def clean_email(self):
        return self.cleaned_data['email'].strip().casefold()
