from django.core.exceptions import ValidationError


def validate_employee_number(value):
    if not value.isdigit():
        raise ValidationError(
                'Employee number should to be only digits.'
            )
    if len(value) != 4:
        raise ValidationError(
                "Employee number must be 4 digits."
            )
    return value
