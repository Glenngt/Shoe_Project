# Generated by Django 4.2.7 on 2023-12-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UrbanShoeApp', '0008_carouselitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerorders',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Order Confirmed', 'Order Confirmed'), ('Out for Pickup', 'Out for Pickup'), ('Stored in Warehouse', 'Stored in Warehouse')], max_length=50, null=True),
        ),
    ]