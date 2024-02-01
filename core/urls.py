from django.urls import path
from .views import RegisterCustomerView, CheckEligibilityView

urlpatterns = [
    path('register_customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('check_eligibility/', CheckEligibilityView.as_view(), name='check_eligibility'),
    # path('create_loan/', CreateLoanView.as_view(), name='create_loan'),
]
