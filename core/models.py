from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2)

    def get_current_debt(self):
        loans = Loan.objects.filter(customer_id=self.customer_id)
        current_debt = sum(loan.get_remaining_amount() for loan in loans)
        return current_debt

    def __str__(self):
        return f"{self.first_name}{self.last_name}"
    

class Loan(models.Model):
    customer_id = models.IntegerField()   
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def get_remaining_amount(self):
        remaining_amount = self.loan_amount
        for emi_number in range(1, self.emis_paid_on_time+1):
            interest_payment = remaining_amount * self.interest_rate / 12 / 100
            principal_payment = self.monthly_repayment - interest_payment
            remaining_amount -= principal_payment
        
        return max(0, remaining_amount)

    def __str__(self):
        return f"Loan #{self.loan_id}"


