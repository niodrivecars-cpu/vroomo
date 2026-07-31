import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django_ratelimit.exceptions import Ratelimited

from .models import Company, UserProfile

logger = logging.getLogger('vroom.ratelimit')

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Cross-Origin-Opener-Policy': 'same-origin',
    'Cross-Origin-Resource-Policy': 'same-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
}


def _build_csp_string(policy):
    """Render a CSP directive dict into a header value string."""
    parts = []
    for directive, sources in policy.items():
        if isinstance(sources, (list, tuple)):
            parts.append(f"{directive} {' '.join(sources)}")
        else:
            parts.append(f"{directive} {sources}")
    return '; '.join(parts)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for key, value in SECURITY_HEADERS.items():
            response[key] = value
        csp_config = getattr(settings, 'SECURITY_CSP', None)
        if csp_config:
            response['Content-Security-Policy-Report-Only'] = _build_csp_string(csp_config)
        return response


class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = UserProfile.objects.select_related('company').filter(user=request.user).first()
            if profile:
                request.company = profile.company
            else:
                default_company, _ = Company.objects.get_or_create(name='Default Company')
                UserProfile.objects.get_or_create(user=request.user, company=default_company)
                request.company = default_company
        else:
            request.company = None
        return self.get_response(request)


class RateLimitLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        limited = getattr(request, 'limited', False)
        if limited:
            self._log_rate_limit(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            self._log_rate_limit(request)
            response = HttpResponse(status=429)
            response['Retry-After'] = '60'
            return response
        return None

    def _log_rate_limit(self, request):
        username = request.user.username if request.user.is_authenticated else 'ANONYMOUS'
        company_id = getattr(request, 'company', None)
        company_id = company_id.pk if company_id else None
        logger.warning(
            'Rate limit exceeded | user=%s | ip=%s | company=%s | path=%s',
            username, request.META.get('REMOTE_ADDR'), company_id, request.path,
        )
        from .models import AuditLog
        AuditLog.objects.create(
            username=username,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            session_key=(request.session.session_key or '') if hasattr(request, 'session') and request.session else '',
            action='RATE_LIMITED',
            change_summary=_('Rate limit exceeded: %(method)s %(path)s') % {'method': request.method, 'path': request.path},
        )
