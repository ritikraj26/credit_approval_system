import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Loan
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer, CheckEligibilitySerializer

class RegisterCustomerView(APIView):
    def post(self, request, format=None):
        serializer = RegisterCustomerSerializer(data=request.data)
        
        if serializer.is_valid():
            customer = Customer.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                age=serializer.validated_data['age'],
                monthly_salary=serializer.validated_data['monthly_income'],
                phone_number=serializer.validated_data['phone_number'],
                approved_limit=0,
                current_debt=0,
            )

            customer.approved_limit = calculate_approved_limit(customer.monthly_salary)
            customer.save()

            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def calculate_approved_limit(monthly_income):
    return round(monthly_income * 36, -5)

class CheckEligibilityView(APIView):
    def get(self, request, format=None):
        serializer = CheckEligibilitySerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            customer = Customer.objects.get(customer_id=customer_id)
            if customer is None:
                return Response("Customer does not exist", status=status.HTTP_400_BAD_REQUEST)

            approval, corrected_interest_rate = self.check_loan_eligibility(customer_id, interest_rate)
            monthly_installment = self.calculate_emi(loan_amount, corrected_interest_rate, tenure)
            response_data = {
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate,
                'tenure': tenure,
                'monthly_installment': monthly_installment,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_loan_eligibility(self, customer_id, interest_rate):
        
        approval = False
        credit_rating = self.calculate_credit_rating(customer_id)
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
    
    def calculate_credit_rating(self, customer_id):
        
        past_loans_paid_on_time = self.get_past_loans_paid_on_time(customer_id)
        number_of_loans_taken = self.get_number_of_loans_taken(customer_id)
        loan_activity_in_current_year = self.get_loan_activity_in_current_year(customer_id)
        loan_approved_volume = self.get_loan_approved_volume(customer_id)

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

    def get_past_loans_paid_on_time(self, customer_id):
        past_loans = Loan.objects.filter(customer_id=customer_id)
        count = 0
        for loan in past_loans:
            if loan.end_date < datetime.date.today():
                if loan.emis_paid_on_time/12 <= loan.tenure:
                    count += 1
        return count

    def get_number_of_loans_taken(self, customer_id):
        return Loan.objects.filter(customer_id=customer_id).count()

    def get_loan_activity_in_current_year(self, customer_id):
        return Loan.objects.filter(customer_id=customer_id, start_date__year=datetime.date.today().year).count()

    def get_loan_approved_volume(self, customer_id):
        return Loan.objects.filter(customer_id=customer_id).count()

    @staticmethod
    def calculate_emi(principal, annual_interest_rate, tenure_in_years):
        monthly_interest_rate = (annual_interest_rate / 12) * 0.01
        tenure_in_months = tenure_in_years * 12
        emi = (principal * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_in_months) / \
            (((1 + monthly_interest_rate) ** tenure_in_months) - 1)
        
        return emi

