from django.urls import path
from .views import read_csv, generate_report, get_report

app_name = 'kitchenMonitoring'

urlpatterns = [
    path('upload/', read_csv, name='upload'),
    path('trigger_report/', generate_report, name='trigger_report'),
    path('get_report/<str:report_id>/', get_report, name='get_report'),
]