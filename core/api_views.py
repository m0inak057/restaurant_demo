from rest_framework import permissions, viewsets

from .models import Category, MenuItem, Order, Table
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
    TableSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):  # type: ignore[override]
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all().order_by("table_number")
    serializer_class = TableSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().select_related("category").order_by("name")
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.all()
        .select_related("table")
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
