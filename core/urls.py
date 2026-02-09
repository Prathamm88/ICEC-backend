from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView, ProfileView,
    EmissionFactorListView,
    ConsumptionRecordListCreateView, ConsumptionRecordDetailView,
    DashboardStatsView, ComparisonView, GenerateReportView
)

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    
    # Emission Factors
    path('factors/', EmissionFactorListView.as_view(), name='emission-factors'),
    
    # Consumption Records
    path('consumption/', ConsumptionRecordListCreateView.as_view(), name='consumption-list-create'),
    path('consumption/<int:pk>/', ConsumptionRecordDetailView.as_view(), name='consumption-detail'),
    
    # Dashboard & Analytics
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/comparison/', ComparisonView.as_view(), name='department-comparison'),
    
    # Reports
    path('report/pdf/', GenerateReportView.as_view(), name='generate-report'),
]
