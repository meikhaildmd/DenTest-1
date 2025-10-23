from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='meikhaildmd',
                email='danielmeikhail@gmail.com',
                password='arnold28'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superuser created.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Superuser already exists.'))