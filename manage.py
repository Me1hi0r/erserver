# !/usr/bin/env python
# """Django's command-line utility for administrative tasks."""

import os
import sys
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ers.settings')
    django.setup()
    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)
