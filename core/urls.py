from django.urls import path
from .views import RegisterCustomer, CheckEligibility, CreateLoan, ViewLoan, ViewLoans

urlpatterns = [
    path('register_customer/', RegisterCustomer.as_view(), name='register_customer'),
    path('check_eligibility/', CheckEligibility.as_view(), name='check_eligibility'),
    path('create_loan/', CreateLoan.as_view(), name='create_loan'),
    path('view_loan/<int:loan_id>/', ViewLoan.as_view(), name='view_loan'),
    path('view_loans/<int:customer_id>/', ViewLoans.as_view(), name='view_loans')
]
