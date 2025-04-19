from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Customer
from datetime import date

class Command(BaseCommand):
    help = 'Creates a Customer profile for the staff user'

    def handle(self, *args, **options):
        try:
            # Get the staff user
            staff_user = User.objects.get(username='staff-sugar')
            
            # Check if the staff user already has a Customer profile
            if not hasattr(staff_user, 'customer'):
                # Create Customer profile for staff
                Customer.objects.create(
                    user=staff_user,
                    name='Sugar Staff',
                    phone='0000000000',
                    email=staff_user.email,
                    address='Sugar Store',
                    line_id='sugar_staff',
                    birthdate=date(2000, 1, 1)  # Default date
                )
                self.stdout.write(self.style.SUCCESS('Successfully created Customer profile for staff-sugar'))
            else:
                self.stdout.write(self.style.WARNING('staff-sugar already has a Customer profile'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('staff-sugar user does not exist')) 