from rest_framework import serializers

from .models import Category, MenuItem, Order, OrderItem, Table


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = [
            "id",
            "table_number",
            "capacity",
            "status",
            "qr_code_url",
            "opened_at",
            "closed_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "description",
            "price",
            "is_available",
            "image",
            "category",
            "category_id",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source="menu_item", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_id",
            "quantity",
            "custom_notes",
            "line_total",
        ]
        read_only_fields = ["line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    table = TableSerializer(read_only=True)
    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(), source="table", write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "table_id",
            "status",
            "total_price",
            "created_at",
            "updated_at",
            "special_instructions",
            "items",
        ]
        read_only_fields = ["total_price", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            order_item = OrderItem.objects.create(order=order, **item_data)
            total += order_item.line_total
        order.total_price = total
        order.save(update_fields=["total_price"])
        # Mark table as occupied and start session if not already
        table = order.table
        if table.status != table.STATUS_OCCUPIED:
            from django.utils import timezone

            table.status = table.STATUS_OCCUPIED
            table.opened_at = timezone.now()
            table.save(update_fields=["status", "opened_at"])
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                order_item = OrderItem.objects.create(order=instance, **item_data)
                total += order_item.line_total
            instance.total_price = total
            instance.save(update_fields=["total_price"])
        return instance
