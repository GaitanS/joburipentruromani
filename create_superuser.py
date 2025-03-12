from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates a superuser with a specified password non-interactively'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'adminpassword'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}" with password "{password}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))

print('Importing Django settings...')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joburipentruromani.settings')

print('Setting up Django...')
import django
django.setup()

print('Creating superuser...')
command = Command()
command.handle()