from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Table(models.Model):
	STATUS_AVAILABLE = "available"
	STATUS_OCCUPIED = "occupied"
	STATUS_RESERVED = "reserved"

	STATUS_CHOICES = [
		(STATUS_AVAILABLE, "Available"),
		(STATUS_OCCUPIED, "Occupied"),
		(STATUS_RESERVED, "Reserved"),
	]

	table_number = models.PositiveIntegerField(unique=True)
	capacity = models.PositiveIntegerField(default=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
	qr_code_url = models.URLField(blank=True)
	opened_at = models.DateTimeField(null=True, blank=True)
	closed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:  # type: ignore[override]
		return f"Table {self.table_number} ({self.get_status_display()})"


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self) -> str:  # type: ignore[override]
		return self.name


class MenuItem(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, related_name="items", on_delete=models.CASCADE)
	is_available = models.BooleanField(default=True)
	image = models.ImageField(upload_to="menu_items/", blank=True, null=True)

	def __str__(self) -> str:  # type: ignore[override]
		return self.name


class Order(models.Model):
	STATUS_RECEIVED = "received"
	STATUS_PREPARING = "preparing"
	STATUS_READY = "ready"
	STATUS_SERVED = "served"
	STATUS_CLOSED = "closed"

	STATUS_CHOICES = [
		(STATUS_RECEIVED, "Received"),
		(STATUS_PREPARING, "Preparing"),
		(STATUS_READY, "Ready"),
		(STATUS_SERVED, "Served"),
		(STATUS_CLOSED, "Closed"),
	]

	table = models.ForeignKey(Table, related_name="orders", on_delete=models.PROTECT)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
	total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	special_instructions = models.TextField(blank=True)
	served_by = models.ForeignKey(
		User,
		related_name="served_orders",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)

	def __str__(self) -> str:  # type: ignore[override]
		return f"Order {self.pk} - Table {self.table.table_number}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
	menu_item = models.ForeignKey(MenuItem, related_name="order_items", on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	custom_notes = models.TextField(blank=True)
	line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def save(self, *args, **kwargs):  # type: ignore[override]
		self.line_total = self.menu_item.price * self.quantity
		super().save(*args, **kwargs)

	def __str__(self) -> str:  # type: ignore[override]
		return f"{self.quantity} x {self.menu_item.name}"


class StaffProfile(models.Model):
	ROLE_ADMIN = "admin"
	ROLE_KITCHEN = "kitchen"
	ROLE_STAFF = "staff"

	ROLE_CHOICES = [
		(ROLE_ADMIN, "Admin"),
		(ROLE_KITCHEN, "Kitchen"),
		(ROLE_STAFF, "Staff"),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)

	def __str__(self) -> str:  # type: ignore[override]
		return f"{self.user.username} ({self.get_role_display()})"

