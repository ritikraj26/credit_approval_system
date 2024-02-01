import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Loan
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer, CheckEligibilitySerializer
from .utils import CheckEligibilityUtils

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

            approval, corrected_interest_rate = CheckEligibilityUtils.check_loan_eligibility(customer_id, interest_rate)
            monthly_installment = CheckEligibilityUtils.calculate_emi(loan_amount, corrected_interest_rate, tenure)
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

    


class CreateLoanView(APIView):
    def post(self, request, format=None):
        pass