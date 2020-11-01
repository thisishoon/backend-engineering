#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from elasticsearch import Elasticsearch, ElasticsearchException
import time

def make_index():
    # es = Elasticsearch(host="host.docker.internal")
    es = Elasticsearch("elasticsearch:9200")
    index = "earthquake"
    while True:
        flag = es.ping()
        if flag:
            print(flag)
            break
        else:
            time.sleep(1)

    time.sleep(5)
    exist = es.indices.exists("earthquake")
    if not exist:
        es.create(index="earthquake")


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
