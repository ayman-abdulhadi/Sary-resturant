from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where employee number is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, employee_number, password=None, **extra_fields):
        """
        Create and save a User with the given employee number and password.
        """
        if not employee_number:
            raise ValueError('The Employee number must be set')
        user = self.model(employee_number=employee_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given
        employee number and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(employee_number, password, **extra_fields)
