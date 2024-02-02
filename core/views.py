import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Loan
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer, CheckEligibilitySerializer
from .utils import CheckEligibilityUtils


class RegisterCustomer(APIView):
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
            print(customer)
            customer.approved_limit = calculate_approved_limit(customer.monthly_salary)
            customer.save()

            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def calculate_approved_limit(monthly_income):
    return round(monthly_income * 36, -5)


class CheckEligibility(APIView):
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

    
class CreateLoan(APIView):
    def post(self, request, format=None):
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
            if not approval:
                return Response("Loan not approved", status=status.HTTP_400_BAD_REQUEST)

            monthly_installment = CheckEligibilityUtils.calculate_emi(loan_amount, corrected_interest_rate, tenure)
            loan = Loan.objects.create(
                customer_id=customer_id,
                loan_amount=loan_amount,
                interest_rate=corrected_interest_rate,
                tenure=tenure,
                monthly_repayment=monthly_installment,
                emis_paid_on_time=0,
                start_date=datetime.date.today(),
                end_date=datetime.date.today() + datetime.timedelta(days=tenure*30),
            )
            loan.save()

            customer.current_debt += loan_amount
            customer.save()

            response_data = {
                'loan_id': loan.loan_id,
                'customer_id': loan.customer_id,
                'loan_approved': approval,
                'message': "Loan approved" if approval else "Loan not approved",
                'monthly_installment': monthly_installment,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ViewLoan(APIView):
    def get(self, request, loan_id, format=None):
        loan = Loan.objects.get(loan_id=loan_id)
        if loan is None:
            return Response("Loan does not exist", status=status.HTTP_400_BAD_REQUEST)
        customer_id = loan.customer_id
        customer = Customer.objects.get(customer_id=customer_id)
        customer_data = {
            'customer_id': customer_id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'age': customer.age,
            'phone_number': customer.phone_number
        }
        response_data = {
            'loan_id': loan.loan_id,
            'customer': customer_data,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'tenure': loan.tenure,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ViewLoans(APIView):
    def get(self, request, customer_id, format=None):
        loans = Loan.objects.filter(customer_id=customer_id)
        if loans is None:
            return Response("Customer does not exist", status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.get(customer_id=customer_id)
        customer_data = {
            'customer_id': customer_id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'age': customer.age,
            'phone_number': customer.phone_number
        }
        response_subdata = []
        for loan in loans:
            
            response_subdata.append({
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'tenure': loan.tenure,
            })
        response_data = {
            'customer': customer_data,
            'loans': response_subdata,
        }
        return Response(response_data, status=status.HTTP_200_OK)