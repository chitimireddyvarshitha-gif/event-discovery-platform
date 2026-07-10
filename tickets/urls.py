from django.urls import path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('<int:ticket_id>/', views.ticket_detail, name='detail'),
    path('organizer/<int:event_id>/', views.organizer_ticket_sales, name='organizer_sales'),
]
