from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm

from django.contrib.auth.models import User
from django import forms
import os
from .models import Bankstatements


class SignupForm(UserCreationForm):
    class Meta:
        model=User
        fields = ('first_name', 'last_name','username', 'email', 'password1', 'password2')

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Your First Name',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Your Last Name',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Your Username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    email = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Your Email',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Repeat Password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

# authenticate user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Your Username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password= forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))


#upload files
def valid_file_extension(value):
    allowed_extensions = ['.csv', '.xls', '.xlsx', '.xlsm']
    extension = os.path.splitext(value.name)[1]  # Get the file extension
    return extension.lower() in allowed_extensions

class UploadFileForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Name your bank statement',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    account = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Name your bank account',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    file = forms.FileField(widget=forms.FileInput(attrs={
        'placeholder':'Only CSV, XLS, XLSX, or XLSM files are allowed.',
        'class': 'w-full py-4 px-6 rounded-xl',
        'accept': ['.csv','.xls','.xlsx','.xlsm']
    }))
    def clean_file(self):
        file = self.cleaned_data['file']
        if not valid_file_extension(file): 
            raise forms.ValidationError('Only CSV, XLS, XLSX, or XLSM files are allowed.')
        return file
    
    def clean_title(self):
        title = self.cleaned_data['title']
        user = self.initial.get('user') 

        # Check if a Bankstatements object with this name already exists for the user
        if Bankstatements.objects.filter(created_by=user, name=title).exists():
            raise forms.ValidationError('A bank statement with this name already exists.')

        return title
    
class EditProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        exclude=['password']

    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)
        if instance:
            for field in self.Meta.fields:
                if cleaned_data.get(field) is None:
                    cleaned_data[field] = getattr(instance, field)
        return cleaned_data
    
