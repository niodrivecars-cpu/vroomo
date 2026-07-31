import os
import uuid

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _

ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
ALLOWED_MIME_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            _('Extension not allowed. Allowed extensions: PDF, PNG, JPG')
        )


def validate_file_size(value):
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            _('File size exceeds the maximum allowed (10 MB)')
        )


def validate_mime_type(value):
    try:
        import magic
        chunk = value.read(2048)
        value.seek(0)
        mime = magic.from_buffer(chunk, mime=True)
        if mime not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                _('File type not allowed. Allowed types: PDF, PNG, JPG')
            )
    except ImportError:
        pass


@deconstructible
class DocumentUploadTo:
    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f'documents/{uuid.uuid4()}{ext}'
