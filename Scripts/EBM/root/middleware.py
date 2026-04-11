"""Custom middleware for the EBM application."""

from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
ATTEMPT_WINDOW = 900    # track attempts within 15 minutes


def _get_client_ip(request):
    """Extract the real client IP from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


class LoginAttemptMiddleware:
    """
    Track failed login attempts per IP address using Django's cache framework.

    After MAX_FAILED_ATTEMPTS failed logins within ATTEMPT_WINDOW seconds,
    the IP is blocked for LOCKOUT_DURATION seconds. A message is shown to
    the user instead of processing the login form.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only intercept POST requests to the login URL
        login_url = reverse('log')
        if request.method == 'POST' and request.path == login_url and 'log' in request.POST:
            ip = _get_client_ip(request)
            lockout_key = f'login_lockout_{ip}'

            if cache.get(lockout_key):
                messages.error(
                    request,
                    'Too many login attempts. Please try again later.',
                    extra_tags='log',
                )
                return redirect(login_url)

        response = self.get_response(request)

        # After the view runs, check if a failed login just occurred
        if request.method == 'POST' and request.path == reverse('log') and 'log' in request.POST:
            ip = _get_client_ip(request)
            lockout_key = f'login_lockout_{ip}'
            attempts_key = f'login_attempts_{ip}'

            # A failed login is indicated by having error messages with 'log' tag
            # and no redirect (i.e., the response is a 200 re-render of the login page)
            if response.status_code == 200:
                attempts = cache.get(attempts_key, 0) + 1
                cache.set(attempts_key, attempts, ATTEMPT_WINDOW)

                if attempts >= MAX_FAILED_ATTEMPTS:
                    cache.set(lockout_key, True, LOCKOUT_DURATION)
                    cache.delete(attempts_key)

            elif response.status_code in (301, 302):
                # Successful login — clear any tracked attempts
                cache.delete(attempts_key)
                cache.delete(lockout_key)

        return response
