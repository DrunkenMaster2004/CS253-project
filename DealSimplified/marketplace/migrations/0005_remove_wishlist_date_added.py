# Generated by Django 5.1.8 on 2025-04-02 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='date_added',
        ),
    ]
