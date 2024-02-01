from django.core.management.base import BaseCommand
from core.models import Customer

class Command(BaseCommand):
    help = 'Calculate and update current debt for all customers'

    def handle(self, *args, **options):
        customers = Customer.objects.all()

        for customer in customers:
            current_debt = customer.get_current_debt()
            customer.current_debt = current_debt
            customer.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated current debt for all customers'))
