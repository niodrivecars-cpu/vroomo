from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language

from fleet.views import (
    CustomLoginView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    health_check,
)

urlpatterns = [
    path('health/', health_check, name='health'),
    path('i18n/setlang/', set_language, name='set_language'),
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('fleet.urls')),
]
