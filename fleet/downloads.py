import logging
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404
from django.utils import timezone
from django_ratelimit.core import is_ratelimited

from .audit import log_audit  # noqa: F401  (re-exported for views)
from .models import VehicleDocument

logger = logging.getLogger(__name__)

TOKEN_VERSION = 1
TOKEN_PURPOSE = 'vehicle_document_download'

# Whitelisted extension -> MIME map. Never trust the client: derive the content
# type from the stored file name, not from any request-supplied value.
EXTENSION_MIME = {
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
}


def _content_type_for_name(name):
    return EXTENSION_MIME.get(Path(name).suffix.lower())


def get_document_or_none(pk, company_id=None):
    qs = VehicleDocument.objects.select_related('vehicle', 'vehicle__company')
    try:
        doc = qs.get(pk=pk)
    except (VehicleDocument.DoesNotExist, ValueError, TypeError):
        return None
    if company_id is not None and doc.vehicle.company_id != company_id:
        return None
    return doc


def decode_token(token):
    """Validate the signed token; return the payload dict or None."""
    if not isinstance(token, str) or not token:
        return None
    try:
        data = signing.loads(token)
    except (signing.BadSignature, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get('v') != TOKEN_VERSION:
        return None
    if data.get('purpose') != TOKEN_PURPOSE:
        return None
    try:
        exp = float(data.get('exp'))
    except (TypeError, ValueError):
        return None
    if timezone.now().timestamp() > exp:
        return None
    return data


def is_download_rate_limited(request):
    """Rate-limit downloads per user (authenticated) or per IP (anonymous).

    Uses the built-in 'user_or_ip' simple key, matching the existing upload
    rate-limit convention. Called directly (not via a blocking decorator) so the
    view can audit the denial before returning 403.
    """
    rate = settings.SECURITY_RATE_LIMITS.get(
        'download_per_user' if request.user.is_authenticated else 'download_anon_ip',
        '20/h',
    )
    return is_ratelimited(
        request=request,
        group='document-download',
        key='user_or_ip',
        rate=rate,
        method='GET',
        increment=True,
    )


def serve_document(doc, request):
    if not doc.file or not doc.file.name:
        raise Http404
    storage = doc.file.storage
    name = doc.file.name
    if not storage.exists(name):
        raise Http404
    content_type = _content_type_for_name(name)
    if content_type is None:
        raise Http404
    try:
        f = storage.open(name, 'rb')
    except OSError:
        logger.exception('Could not open document %s', name)
        raise Http404
    filename = doc.original_filename or Path(name).name
    ascii_name = filename.encode('ascii', 'ignore').decode() or 'download'
    response = FileResponse(f, content_type=content_type)
    response['Content-Disposition'] = (
        f"attachment; filename=\"{ascii_name}\"; "
        f"filename*=UTF-8''{quote(filename)}"
    )
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
