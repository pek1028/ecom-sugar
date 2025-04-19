from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from collections import defaultdict

class Command(BaseCommand):
    help = 'Cleans up duplicate users with the same email address'

    def handle(self, *args, **options):
        # Find all users with duplicate emails
        email_users = defaultdict(list)
        for user in User.objects.all():
            if user.email:
                email_users[user.email].append(user)

        # Process duplicates
        for email, users in email_users.items():
            if len(users) > 1:
                self.stdout.write(f'Found {len(users)} users with email: {email}')
                
                # Keep the first user and delete others
                keep_user = users[0]
                for user in users[1:]:
                    self.stdout.write(f'Deleting user: {user.username}')
                    user.delete()
                
                self.stdout.write(f'Kept user: {keep_user.username}')

        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate users')) 