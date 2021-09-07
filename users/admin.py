from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        'employee_number', 'name', 'role', 'is_staff', 'is_active',
    )
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('employee_number', 'password', 'name', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'employee_number', 'password1', 'password2',
                    'name', 'role', 'is_staff', 'is_active'
                )
            }
        ),
    )
    search_fields = ('employee_number',)
    ordering = ('employee_number',)


admin.site.register(User, CustomUserAdmin)
