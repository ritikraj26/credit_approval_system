# core/management/commands/ingestdata.py

from django.core.management.base import BaseCommand
from core.models import Customer, Loan
import pandas as pd
from decimal import Decimal

class Command(BaseCommand):
    help = 'Ingest loan data from excel files into the database'

    def handle(self, *args, **options):
        try:
            loan_data = pd.read_excel('files/loan_data.xlsx')

            for _, row in loan_data.iterrows():
                loan_id = int(row.get('Loan ID'))
                if Loan.objects.filter(loan_id=loan_id).exists():
                    continue
                Loan.objects.create(
                    customer_id=int(row.get('Customer ID')),
                    loan_id=int(row.get('Loan ID')),
                    loan_amount=Decimal(row.get('Loan Amount')),
                    tenure=int(row.get('Tenure')),
                    interest_rate=Decimal(row.get('Interest Rate')),
                    monthly_repayment=Decimal(row.get('Monthly payment')),
                    emis_paid_on_time=int(row.get('EMIs paid on Time')),
                    start_date=row.get('Date of Approval'),
                    end_date=row.get('End Date'),
                )
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            raise e
