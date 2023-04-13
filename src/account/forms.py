from django import forms
from django.contrib.auth import password_validation
from utils.base.validators import validate_special_char
from utils.base.constants import User


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=8,
        help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        help_text='Must be similar to first password to pass verification')
    fullname = forms.CharField(
        label="Fullname",
        help_text="Enter your fullname",
        validators=[validate_special_char],
    )

    class Meta:
        model = User
        fields = (
            "email", "username",
            "password", "password2",
            "fullname"
        )

    def clean_password(self):
        """Cleaning password one to check if
        all validations are met
        """

        ps1 = self.cleaned_data.get("password")
        password_validation.validate_password(ps1, None)
        return ps1

    def clean_password2(self):
        """Override clean on password2 level to
        compare similarities of password
        """

        ps1 = self.cleaned_data.get("password")
        ps2 = self.cleaned_data.get("password2")
        if (ps1 and ps2) and (ps1 != ps2):
            raise forms.ValidationError("The passwords does not match")
        return ps2

    def save(self, commit=True):
        """
        Override the default save method to use set_password
        method to convert text to hashed
        """
        user: User = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("password"))

        if commit:
            user.save()

            # Profile is already created, update values with data in form
            profile = user.profile
            profile.fullname = self.cleaned_data.get('fullname')
            profile.save()

        return user
