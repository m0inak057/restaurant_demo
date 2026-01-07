from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.menu_page, name="menu"),
    path("order/", views.order_page, name="order"),  # expects ?table=<id>
    path("order/track/<int:order_id>/", views.order_status_page, name="order_status"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
]
