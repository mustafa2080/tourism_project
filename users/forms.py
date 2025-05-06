from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import CustomUser

# استيرادات أخرى للفورمات العادية
class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class UserProfileForm(forms.ModelForm):
    """Form for users to update their own profile information."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            pass  # Placeholder for styling

# فورم الـ Signup المخصصة
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    username = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        """Validate email uniqueness for signup"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Check if email already exists
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError(_('This email address is already registered. Please use a different email or log in.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        if 'password1' in cleaned_data and 'password2' in cleaned_data:
            if cleaned_data['password1'] != cleaned_data['password2']:
                raise forms.ValidationError(_("Passwords don't match"))

        # Generar automáticamente el nombre de usuario a partir del correo electrónico
        if 'email' in cleaned_data:
            email_username = cleaned_data['email'].split('@')[0]
            # Asegurarse de que el nombre de usuario sea único
            base_username = email_username
            counter = 1
            while CustomUser.objects.filter(username=email_username).exists():
                email_username = f"{base_username}{counter}"
                counter += 1
            cleaned_data['username'] = email_username

        return cleaned_data

# فورم الـ Login المخصصة
class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom attributes or modify fields if needed
        self.fields['login'].label = _('Email Address')
        self.fields['login'].widget.attrs.update({'placeholder': _('Enter your email')})
        self.fields['password'].widget.attrs.update({'placeholder': _('Enter your password')})

    def clean_login(self):
        """Comprehensive email validation for login"""
        email = self.cleaned_data.get('login')
        if not email:
            raise ValidationError(_('Email address is required.'))

        # Normalize the email (lowercase)
        email = email.lower().strip()

        # Check email length
        if len(email) < 6:
            raise ValidationError(_('Email must be at least 6 characters long.'))
        if len(email) > 254:
            raise ValidationError(_('Email cannot exceed 254 characters.'))

        # Basic format validation
        if '@' not in email:
            raise ValidationError(_('Email must contain an \'@\' symbol.'))

        # Split email into username and domain parts
        try:
            username, domain = email.split('@')
        except ValueError:
            raise ValidationError(_('Email must contain exactly one \'@\' symbol.'))

        # Username validation
        if not username:
            raise ValidationError(_('Username part of email cannot be empty.'))

        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            raise ValidationError(_('Username can only contain letters, numbers, dots, hyphens, or underscores.'))

        # Check for consecutive special characters in username
        if re.search(r'\.{2,}|-{2,}|_{2,}|\.\-|\-\.|\._|_\.', username):
            raise ValidationError(_('Username cannot contain consecutive special characters.'))

        # Domain validation
        if not domain:
            raise ValidationError(_('Domain part of email cannot be empty.'))

        if '.' not in domain:
            raise ValidationError(_('Domain must include a dot for the top-level domain.'))

        # Check domain format
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            raise ValidationError(_('Domain must be valid and include a top-level domain.'))

        # Check for consecutive special characters in domain
        if re.search(r'\.{2,}|-{2,}|\.\-|\-\.', domain):
            raise ValidationError(_('Domain cannot contain consecutive special characters.'))

        # Check top-level domain (TLD)
        tld = domain.split('.')[-1].lower()

        # List of valid TLDs
        valid_tlds = [
            'com', 'net', 'org', 'edu', 'gov', 'mil', 'io', 'co.uk', 'ca', 'de',
            'fr', 'jp', 'au', 'nz', 'ru', 'it', 'es', 'nl', 'br', 'in', 'mx',
            'ch', 'se', 'no', 'dk', 'fi', 'pl', 'cz', 'hu', 'pt', 'gr', 'ie',
            'at', 'hk', 'sg', 'ae', 'za', 'ar', 'cl', 'pe', 'co', 've', 'ua',
            'tr', 'sa', 'eg', 'th', 'my', 'ph', 'vn', 'id', 'kr', 'il', 'info',
            'biz', 'me', 'tv', 'app', 'dev', 'io', 'ai', 'cloud', 'design',
            'online', 'store', 'tech', 'blog', 'site', 'xyz'
        ]

        # Disallowed standalone TLDs
        disallowed_tlds = ['co']

        if tld in disallowed_tlds:
            raise ValidationError(
                _('Invalid top-level domain: \'.{0}\' is not allowed. Use a complete domain like \'.com\'.').format(tld)
            )

        if tld not in valid_tlds:
            raise ValidationError(
                _('Invalid top-level domain: \'.{0}\' is not recognized.').format(tld)
            )

        # Check if the email exists in the database (for login)
        User = get_user_model()
        if not User.objects.filter(email__iexact=email).exists():
            # Use a generic error message to avoid revealing which emails are registered
            # This is a security best practice to prevent user enumeration
            raise ValidationError(_('The email or password you entered is incorrect.'))

        return email

    def save(self, request):
        # El nombre de usuario ya se ha generado en el método clean
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user