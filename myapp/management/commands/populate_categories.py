from django.core.management.base import BaseCommand
from myapp.models import Category

class Command(BaseCommand):
    help = 'Populate the Category model with predefined categories'

    def handle(self, *args, **kwargs):
        categories = [
            "上衣",
            "褲子",
            "裙子",
            "套裝",  # Note: Should include "褲子&裙子"
            "小可愛",
            "背心",
            "外套",  # Note: Should include "厚&薄&西裝"
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
            self.stdout.write(self.style.SUCCESS(f"Added category: {category_name}"))

        self.stdout.write(self.style.SUCCESS("All categories have been populated."))