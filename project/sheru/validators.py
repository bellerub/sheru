from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

def validate_absolute_path(value):
    if not os.path.isabs(value):
        raise ValidationError(
            _('%(value)s is not an absolute path'),
            params={'value': value},
        )