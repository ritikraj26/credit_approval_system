from django.urls import path
from .views import RegisterCustomerView, CheckEligibilityView, CreateLoanView, ViewLoanView, ViewLoansView

urlpatterns = [
    path('register_customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('check_eligibility/', CheckEligibilityView.as_view(), name='check_eligibility'),
    path('create_loan/', CreateLoanView.as_view(), name='create_loan'),
    path('view_loan/<int:loan_id>/', ViewLoanView.as_view(), name='view_loan'),
    path('view_loans/<int:customer_id>/', ViewLoansView.as_view(), name='view_loans')
]
