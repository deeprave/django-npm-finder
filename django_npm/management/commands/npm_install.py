from django.core.management.base import BaseCommand, CommandError

from django_npm.finders import npm_install


class Command(BaseCommand):
    help = "Run npm install"

    def handle(self, *args, **options):
        try:
            returncode = npm_install()
        except OSError as exc:
            raise CommandError(f"Could not run the package manager: {exc}") from exc
        if returncode:
            raise CommandError(f"The package manager failed with exit code {returncode}")
