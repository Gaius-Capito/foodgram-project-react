import re

from django.core.exceptions import ValidationError


def validate_real_name(value):

    reg = r'^[\w-]+\Z'

    if not re.fullmatch(reg, value):
        raise ValidationError({
            'Неверное значение имени пользователя'})
