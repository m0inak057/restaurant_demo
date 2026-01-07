from django.contrib import admin

from .models import Category, MenuItem, Order, OrderItem, StaffProfile, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
	list_display = ("table_number", "capacity", "status", "opened_at", "closed_at")
	list_filter = ("status",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "price", "is_available")
	list_filter = ("category", "is_available")


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "table", "status", "total_price", "created_at", "updated_at")
	list_filter = ("status", "table")
	inlines = [OrderItemInline]


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role")
	list_filter = ("role",)

