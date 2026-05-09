import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, connections


class Command(BaseCommand):
    help = "Wait until the default database is available."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_connection = connections["default"]

        while True:
            try:
                db_connection.ensure_connection()
                break
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available."))
