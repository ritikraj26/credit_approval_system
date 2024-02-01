from .models import Customer, Loan
import datetime

class CheckEligibilityUtils:
    
    @staticmethod
    def check_loan_eligibility(  customer_id, interest_rate):
        
        approval = False
        credit_rating = CheckEligibilityUtils.calculate_credit_rating(customer_id)
        corrected_interest_rate = interest_rate

        if credit_rating >= 50:
            approval = True
        elif credit_rating >= 30 and credit_rating < 50:
            corrected_interest_rate = max(12, interest_rate)
            approval = True
        elif credit_rating >= 10 and credit_rating < 30:
            corrected_interest_rate = max(16, interest_rate)
            approval = True
        else:
            approval = False
        
        total_monthly_emi = 0
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer_id=customer_id)
        for loan in loans:
            if loan.end_date > datetime.date.today():
                total_monthly_emi += loan.monthly_repayment

        if total_monthly_emi > customer.monthly_salary/2:
            approval = False

        return approval, corrected_interest_rate
    
    @staticmethod
    def calculate_credit_rating( customer_id):
        
        past_loans_paid_on_time = CheckEligibilityUtils.get_past_loans_paid_on_time(customer_id)
        number_of_loans_taken = CheckEligibilityUtils.get_number_of_loans_taken(customer_id)
        loan_activity_in_current_year = CheckEligibilityUtils.get_loan_activity_in_current_year(customer_id)
        loan_approved_volume = CheckEligibilityUtils.get_loan_approved_volume(customer_id)

        weight_past_loans_paid_on_time = 0.4
        weight_number_of_loans_taken = 0.3
        weight_loan_activity_in_current_year = 0.2
        weight_loan_approved_volume = 0.1

        credit_rating = (
            (past_loans_paid_on_time * weight_past_loans_paid_on_time) +
            (number_of_loans_taken * weight_number_of_loans_taken) +
            (loan_activity_in_current_year * weight_loan_activity_in_current_year) +
            (loan_approved_volume * weight_loan_approved_volume)
        )

        customer = Customer.objects.get(customer_id=customer_id)
        if customer.get_current_debt() > customer.approved_limit:
            credit_rating = 0
        return credit_rating

    @staticmethod
    def get_past_loans_paid_on_time( customer_id):
        past_loans = Loan.objects.filter(customer_id=customer_id)
        count = 0
        for loan in past_loans:
            if loan.end_date < datetime.date.today():
                if loan.emis_paid_on_time/12 <= loan.tenure:
                    count += 1
        return count

    @staticmethod
    def get_number_of_loans_taken( customer_id):
        return Loan.objects.filter(customer_id=customer_id).count()

    @staticmethod
    def get_loan_activity_in_current_year( customer_id):
        return Loan.objects.filter(customer_id=customer_id, start_date__year=datetime.date.today().year).count()

    @staticmethod
    def get_loan_approved_volume( customer_id):
        return Loan.objects.filter(customer_id=customer_id).count()

    @staticmethod
    def calculate_emi(principal, annual_interest_rate, tenure_in_years):
        monthly_interest_rate = (annual_interest_rate / 12) * 0.01
        tenure_in_months = tenure_in_years * 12
        emi = (principal * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_in_months) / \
            (((1 + monthly_interest_rate) ** tenure_in_months) - 1)
        
        return emi