from decimal import Decimal

from django.db import migrations


def seed_menu(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    MenuItem = apps.get_model("core", "MenuItem")

    # If there are already menu items, don't seed again
    if MenuItem.objects.exists():
        return

    categories_data = {
        "Veg": [
            ("Paneer Tikka", "Char-grilled cottage cheese with North Indian spices.", Decimal("260")),
            ("Veg Manchurian", "Crispy vegetable dumplings tossed in Indo-Chinese sauce.", Decimal("220")),
        ],
        "Snacks": [
            ("Veg Pakora Platter", "Assorted seasonal vegetable fritters.", Decimal("180")),
            ("Paneer Kathi Roll", "Soft rumali roti with paneer tikka filling.", Decimal("200")),
        ],
        "Main Course": [
            ("Dal Tadka", "Yellow lentils tempered with ghee, garlic and spices.", Decimal("190")),
            ("Paneer Butter Masala", "Rich tomato and cashew gravy with soft paneer cubes.", Decimal("260")),
            ("Veg Biryani", "Fragrant basmati rice with vegetables and whole spices.", Decimal("260")),
            ("Steamed Rice", "Plain basmati steamed rice.", Decimal("140")),
            ("Butter Naan", "Soft tandoor baked naan brushed with butter.", Decimal("50")),
            ("Garlic Naan", "Tandoor baked naan with garlic and coriander.", Decimal("70")),
        ],
        "Drinks": [
            ("Masala Chaas", "Spiced buttermilk with roasted cumin and coriander.", Decimal("80")),
            ("Sweet Lassi", "Classic sweet yoghurt-based drink.", Decimal("110")),
            ("Cold Coffee", "Chilled coffee with milk and ice cream.", Decimal("150")),
            ("Lemon Iced Tea", "Refreshing iced tea with lemon.", Decimal("130")),
        ],
    }

    for cat_name, items in categories_data.items():
        category, _ = Category.objects.get_or_create(name=cat_name)
        for name, description, price in items:
            MenuItem.objects.get_or_create(
                name=name,
                category=category,
                defaults={
                    "description": description,
                    "price": price,
                    "is_available": True,
                },
            )


def unseed_menu(apps, schema_editor):
    # Keep it simple: do nothing on reverse to avoid deleting real data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_menu, reverse_code=unseed_menu),
    ]
