#!/usr/bin/env python
import os
import sys
from gevent import monkey
monkey.patch_all(thread=False, select=False)

if __name__ == "__main__":
    """
    This is a special version of manage.py for run_add_missing_pand.
    This version imports gevent and  does the  monkey patching.
    We do not want to do that for all other tasks.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monumenten.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
