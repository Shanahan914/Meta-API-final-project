# Generated by Django 5.0.7 on 2024-07-20 17:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0003_menuitems_inventory"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name="CartItems", new_name="CartItem",),
        migrations.RenameModel(old_name="Categories", new_name="Category",),
        migrations.RenameModel(old_name="MenuItems", new_name="MenuItem",),
        migrations.RenameModel(old_name="Orders", new_name="Order",),
        migrations.RenameModel(old_name="OrderItems", new_name="OrderItem",),
    ]
