# core/management/commands/ingestdata.py

from django.core.management.base import BaseCommand
from core.models import Customer, Loan
import pandas as pd
from decimal import Decimal

class Command(BaseCommand):
    help = 'Ingest customer data from excel files into the database'

    def handle(self, *args, **options):
        try:
            customer_data = pd.read_excel('files/customer_data.xlsx')

            print(customer_data)
            for _, row in customer_data.iterrows():
                Customer.objects.create(
                    first_name=str(row.get('First Name')),
                    last_name=str(row.get('Last Name')),
                    age=int(row.get('Age')),
                    phone_number=str(row.get('Phone Number')),
                    monthly_salary=Decimal(row.get('Monthly Salary')),
                    approved_limit=Decimal(row.get('Approved Limit')),
                    current_debt=Decimal(row.get('Current Debt','0.0')),
                )
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            raise e
