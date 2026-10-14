"""Create a limited MySQL login for the public, disposable teaching demo."""

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Create the limited external MySQL user for the Railway teaching demo"

    def handle(self, *args, **options):
        if connection.vendor != "mysql" or connection.settings_dict["NAME"] != "little_paws_net_demo":
            raise CommandError("This command is restricted to the MySQL teaching demo")

        password = os.environ.get("LPN_DEMO_DB_PASSWORD", "")
        if len(password) < 24:
            raise CommandError("Set a random LPN_DEMO_DB_PASSWORD of at least 24 characters")

        with connection.cursor() as cursor:
            cursor.execute("CREATE USER IF NOT EXISTS 'lpn_docente_demo'@'%' IDENTIFIED BY %s", [password])
            cursor.execute("ALTER USER 'lpn_docente_demo'@'%' IDENTIFIED BY %s", [password])
            cursor.execute("GRANT SELECT ON `little_paws_net_demo`.* TO 'lpn_docente_demo'@'%'")
            cursor.execute(
                "GRANT INSERT, UPDATE, DELETE ON `little_paws_net_demo`.`django_session` "
                "TO 'lpn_docente_demo'@'%'"
            )
            cursor.execute(
                "GRANT UPDATE (`last_login`) ON `little_paws_net_demo`.`Usuario` "
                "TO 'lpn_docente_demo'@'%'"
            )

        self.stdout.write(self.style.SUCCESS("Limited external demo user configured"))
