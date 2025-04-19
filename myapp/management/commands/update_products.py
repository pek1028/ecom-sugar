from django.core.management.base import BaseCommand
from myapp.models import Product

class Command(BaseCommand):
    help = 'Update existing products with default size and color values'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            # Set a default size if empty
            if not product.size:
                product.size = 'm'  # Default to medium
            # Set a default color if empty
            if not product.color:
                product.color = 'Black'  # Default color
            product.save()
            self.stdout.write(self.style.SUCCESS(f"Updated product: {product.name}"))

        self.stdout.write(self.style.SUCCESS("All products have been updated."))