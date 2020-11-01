#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from elasticsearch import Elasticsearch, ElasticsearchException


def make_index():
    es = Elasticsearch(host="host.docker.internal")
    index = "earthquake"
    while True:
        flag = es.ping()
        if flag:
            print(flag)
            break
    if es.indices.exists(index=index):
        print('existing earthquake index in use')
    else:
        es.indices.create(index=index)
        print("earthquake index is created")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api2.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    make_index()
    main()
