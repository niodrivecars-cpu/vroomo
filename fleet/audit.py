from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from django.utils.translation import gettext as _


def log_audit(request, action, obj=None, summary=''):
    from .models import AuditLog
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        session_key=request.session.session_key or '',
        action=action,
        content_type=obj._meta.label if obj else '',
        object_id=str(obj.pk) if obj else '',
        object_repr=str(obj)[:200] if obj else '',
        change_summary=summary,
    )


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        user=user,
        username=user.get_username(),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        session_key=(request.session.session_key or '') if request.session else '',
        action='LOGIN',
        change_summary=_('Login: %(user)s') % {'user': user.get_username()},
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        user=user,
        username=user.get_username() if user else 'ANONYMOUS',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        session_key=(request.session.session_key or '') if request.session else '',
        action='LOGOUT',
        change_summary=_('Logout: %(user)s') % {'user': user.get_username() if user else _('Anonymous')},
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        username=credentials.get('username', 'UNKNOWN'),
        ip_address=request.META.get('REMOTE_ADDR') if request else '',
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
        session_key=(request.session.session_key or '') if request and request.session else '',
        action='LOGIN_FAILED',
        change_summary=_('Failed login: %(user)s') % {'user': credentials.get('username', '')},
    )
