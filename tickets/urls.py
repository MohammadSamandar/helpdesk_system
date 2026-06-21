from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    # آدرس صفحه اصلی لیست تیکت ها
    path('', views.index, name='index'),

    # آدرس صفحه جزییات یک تیکت خاص
    path('ticket/<int:ticket_id>', views.ticket_by_id, name='ticket_by_id'),

    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('create/', views.create_ticket, name='create_ticket'),

    # برای کارشناسان
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/<int:ticket_id>/assign/', views.assigne_ticket, name='assign_ticket'),
    path('ticket/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('ticket/<int:ticket_id>/reopen/', views.reopen_ticket, name='reopen_ticket'),


]
