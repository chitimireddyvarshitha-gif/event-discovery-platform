from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.reports_dashboard, name='reports'),
    path('chart-data/', views.chart_data_api, name='chart_data'),
]
