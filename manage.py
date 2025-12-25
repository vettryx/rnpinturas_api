#!/usr/bin/env python
# manage.py

"""Django's command-line utility for administrative tasks."""
import os
import sys

import pymysql
from django.core.management import execute_from_command_line

# Configurações do MySQL
pymysql.version_info = (2, 2, 7, "final", 0)
pymysql.install_as_MySQLdb()

# Define os settings ANTES de rodar o main, no escopo global
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rnpinturas.settings')

def main():
    """Run administrative tasks."""
    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__ == '__main__':
    main()
