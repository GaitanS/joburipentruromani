from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm):
    """Form for job seeker registration"""
    first_name = forms.CharField(max_length=30, required=True, label=_('Prenume'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Nume'))
    email = forms.EmailField(max_length=254, required=True, label=_('Email'))
    phone = forms.CharField(max_length=15, required=False, label=_('Telefon'))
    terms = forms.BooleanField(required=True, label=_('Termeni și condiții'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Această adresă de email este deja utilizată.'))
        return email


class CompanyRegistrationForm(UserCreationForm):
    """Form for employer/company registration"""
    first_name = forms.CharField(max_length=30, required=True, label=_('Prenume contact'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Nume contact'))
    email = forms.EmailField(max_length=254, required=True, label=_('Email'))
    phone = forms.CharField(max_length=15, required=True, label=_('Telefon'))
    company_name = forms.CharField(max_length=100, required=True, label=_('Nume companie'))
    website = forms.URLField(max_length=200, required=False, label=_('Website'))
    terms = forms.BooleanField(required=True, label=_('Termeni și condiții'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Această adresă de email este deja utilizată.'))
        return email
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        from .models import Company
        if Company.objects.filter(name=company_name).exists():
            raise forms.ValidationError(_('Există deja o companie cu acest nume.'))
        return company_name


class JobSeekerProfileForm(forms.Form):
    """Form for updating job seeker profile"""
    first_name = forms.CharField(max_length=30, required=True, label=_('Prenume'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Nume'))
    email = forms.EmailField(max_length=254, required=True, label=_('Email'))
    phone = forms.CharField(max_length=15, required=False, label=_('Telefon'))
    bio = forms.CharField(widget=forms.Textarea, required=False, label=_('Despre mine'))
    skills = forms.CharField(widget=forms.Textarea, required=False, label=_('Abilități'))
    experience = forms.CharField(widget=forms.Textarea, required=False, label=_('Experiență'))
    education = forms.CharField(widget=forms.Textarea, required=False, label=_('Educație'))
    profile_picture = forms.ImageField(required=False, label=_('Poză de profil'))