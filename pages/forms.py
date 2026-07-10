from django import forms
from django.contrib.auth import get_user_model
from fixpoint_backend.users.models import Role, DEPARTMENT_CHOICES
from fixpoint_backend.issues.models import Issue

User = get_user_model()


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'category', 'priority', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief, descriptive title for the issue…'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 5,
                'placeholder': 'Describe the issue in detail. Include steps to reproduce, expected behavior, and actual behavior…'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default priority
        if not self.instance.pk:
            self.fields['priority'].initial = 'MEDIUM'

        # Category choices
        self.fields['category'].choices = [
            ('', 'Select category…'),
            ('TECHNICAL', 'Technical'),
            ('BILLING', 'Billing'),
            ('GENERAL', 'General'),
            ('OTHER', 'Other'),
        ]

        # Priority choices
        self.fields['priority'].choices = [
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
        ]