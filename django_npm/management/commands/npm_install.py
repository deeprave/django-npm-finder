from django.core.management.base import BaseCommand

from django_npm.finders import npm_install


class Command(BaseCommand):
    help = "Run npm install"

    def handle(self, *args, **options):
        npm_install()
