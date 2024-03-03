# Generated by Django 4.2.7 on 2023-12-15 07:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('UrbanShoeApp', '0012_delete_carouselitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellercart',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sellercarts', to=settings.AUTH_USER_MODEL),
        ),
    ]
