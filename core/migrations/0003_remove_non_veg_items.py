from django.db import migrations


def remove_non_veg_items(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    MenuItem = apps.get_model("core", "MenuItem")

    non_veg_names = [
        "Chicken Tikka",
        "Tandoori Chicken (Half)",
        "Chicken Kathi Roll",
        "Chicken Butter Masala",
        "Mutton Rogan Josh",
        "Chicken Biryani",
    ]

    MenuItem.objects.filter(name__in=non_veg_names).delete()
    Category.objects.filter(name="Non Veg").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_seed_menu"),
    ]

    operations = [
        migrations.RunPython(remove_non_veg_items, reverse_code=migrations.RunPython.noop),
    ]
