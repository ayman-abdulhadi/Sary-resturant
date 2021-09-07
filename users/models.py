from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager
from users.utils import validate_employee_number


class User(AbstractBaseUser, PermissionsMixin):
    ROLES_CHOICES = (
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
    )

    employee_number = models.CharField(
                        max_length=4,
                        unique=True,
                        validators=[validate_employee_number],
                        error_messages={
                            'unique':
                            "A user with that employee number already exists."
                        }
                    )
    name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(
                max_length=10,
                choices=ROLES_CHOICES,
                default='Employee'
            )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_number'

    def __str__(self):
        return self.employee_number
