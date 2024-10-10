from django import forms
from .models import Seccion, Sala


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = '__all__'

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = '__all__'