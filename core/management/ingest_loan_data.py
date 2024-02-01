# core/management/commands/ingestdata.py

from django.core.management.base import BaseCommand
from core.models import Customer, Loan
import pandas as pd
from decimal import Decimal

class Command(BaseCommand):
    help = 'Ingest loan data from excel files into the database'

    def handle(self, *args, **options):
        try:
            loan_data = pd.read_excel('loan_data.xlsx')

            # for _, row in loan_data.iterrows():
            #     Loan.objects.create(
            #         customer_id=int(row.get('customer_id')),
            #         loan_amount=Decimal(row.get('loan_amount')),
            #         tenure=row.get('tenure'),
            #         interest_rate=Decimal(row.get('interest_rate')),
            #         monthly_repayment=Decimal(row.get('monthly_repayment')),
            #         emis_paid_on_time=int(row.get('emis_paid_on_time')),
            #         start_date=row.get('start_date'),
            #         end_date=row.get('end_date'),
            #     )
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            raise e
