from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext as _


def staff_required(view_func=None, template_name='fleet/forbidden.html'):
    def decorator(f):
        @wraps(f)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_staff:
                return f(request, *args, **kwargs)
            return render(request, template_name, {
                'message': _('You do not have permission to access this page'),
            }, status=403)
        return _wrapped
    if view_func:
        return decorator(view_func)
    return decorator


def forbidden(request, message=None):
    if message is None:
        message = _('You do not have permission to access this page')
    return render(request, 'fleet/forbidden.html', {'message': message}, status=403)
