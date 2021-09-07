from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('employee_number', 'name', 'role')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('employee_number', 'name', 'role')
