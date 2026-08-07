"""
Passenger WSGI entrypoint for Hostinger shared hosting.

Hostinger's Passenger expects a module-level ``application`` in this file at
the app root. It reads the same settings and .env file as every other process.

Entry point configured in hPanel -> Python App -> "Entry point": passenger_wsgi.py
"""

from config.wsgi import application  # noqa: F401  (re-exported for Passenger)
